from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3
import json

# =========================================================
#  FASTAPI AYARLARI
# =========================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend adresini buraya yazabilirsin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
#  BLOCKCHAIN AYARLARI
# =========================================================
SEPOLIA_RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/NUXpZx9wdu7MNMCXnTAQ5"
CONTRACT_ADDRESS = "0x5f81bD4460FeC194417E10d2821d9Dee69B7Df00"
PRIVATE_KEY = "b6a6c588e0f5656cb6ce2f32741ef0705c3bf30c6e725c592e32675c611755a4"
CHAIN_ID = 11155111

# =========================================================
#  CONTRACT ABI
# =========================================================
CONTRACT_ABI = json.loads('''[
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": false, "internalType": "uint256", "name": "kartId", "type": "uint256"},
            {"indexed": false, "internalType": "address", "name": "sahip", "type": "address"}
        ],
        "name": "KartBasildi",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "address", "name": "_alici", "type": "address"}],
        "name": "yeniKartBas",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "kartSahibi",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "toplamKartSayisi",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]''')

# =========================================================
#  WEB3 BAĞLANTISI
# =========================================================
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL, request_kwargs={'timeout': 10}))
if not w3.is_connected():
    print("❌ Web3 RPC Bağlantısı Başarısız!")
    exit()

account = w3.eth.account.from_key(PRIVATE_KEY)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# =========================================================
#  MODELLER
# =========================================================
class MintModel(BaseModel):
    alici_adres: str

# =========================================================
#  ANA SAYFA
# =========================================================
@app.get("/")
def home():
    return {"message": "Backend Çalışıyor!"}

# =========================================================
#  TOPLAM KART SAYISI
# =========================================================
@app.get("/card/count")
def get_card_count():
    try:
        total = contract.functions.toplamKartSayisi().call()
        return {"total": total}
    except Exception as e:
        print(f"❌ HATA: toplamKartSayisi çağrılırken: {e}")
        raise HTTPException(status_code=500, detail="Kart sayısı okunamadı.")

# =========================================================
#  KART BASMA (MINT)
# =========================================================
@app.post("/card/mint")
def mint_card(data: MintModel):
    alici = data.alici_adres

    try:
        # Checksum address kullan
        alici = w3.to_checksum_address(alici)

        nonce = w3.eth.get_transaction_count(account.address)
        block = w3.eth.get_block("latest")
        base_fee = block["baseFeePerGas"]
        priority_fee = w3.to_wei(2, "gwei")
        max_fee = base_fee + priority_fee + w3.to_wei(5, "gwei")

        tx = contract.functions.yeniKartBas(alici).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "chainId": CHAIN_ID,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee
        })

        tx["gas"] = w3.eth.estimate_gas(tx)
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)  # ✅ düzeltildi
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            "tx_hash": w3.to_hex(tx_hash),
            "status": receipt.status
        }

    except Exception as e:
        print(f"❌ Mint Hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Mint işlemi başarısız: {e}")
