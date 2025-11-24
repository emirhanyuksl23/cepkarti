from web3 import Web3
import json

# =========================================================
#               AYAR BİLGİLERİ (DOLDURACAKSIN)
# =========================================================

SEPOLIA_RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/NUXpZx9wdu7MNMCXnTAQ5"
CONTRACT_ADDRESS = "0x5f81bD4460FeC194417E10d2821d9Dee69B7Df00"
PRIVATE_KEY = "b6a6c588e0f5656cb6ce2f32741ef0705c3bf30c6e725c592e32675c611755a4"
ALICI_ADRES = "0x7FDdCD8C0cd707fB596037f36572912103985e50"
CHAIN_ID = 11155111

# ABI'ni buraya yapıştır
CONTRACT_ABI = json.loadsCONTRACT_ABI = json.loads('''
[
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "kartId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "sahip",
				"type": "address"
			}
		],
		"name": "KartBasildi",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_alici",
				"type": "address"
			}
		],
		"name": "yeniKartBas",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "kartSahibi",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "toplamKartSayisi",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "yonetici",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
''')

# =========================================================


# AĞA BAĞLAN
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))

if not w3.is_connected():
    print("❌ RPC bağlantısı kurulamadı!")
    exit()

print("✅ Sepolia'ya bağlanıldı.")

# HESAP
account = w3.eth.account.from_key(PRIVATE_KEY)
print("👛 Cüzdan:", account.address)

# CONTRACT
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)


# =========================================================
#                MINT FONKSİYONU (HATASIZ)
# =========================================================
def mint(alici):
    print(f"\n➡️ Mint başlatılıyor: {alici}")

    nonce = w3.eth.get_transaction_count(account.address)

    # GAS AYARLARI (EIP-1559)
    block = w3.eth.get_block("latest")
    base_fee = block["baseFeePerGas"]
    priority_fee = w3.to_wei(2, "gwei")
    max_fee = base_fee + priority_fee + w3.to_wei(5, "gwei")

    # İşlem hazırlama
    tx = contract.functions.yeniKartBas(alici).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": priority_fee
    })

    # GAS TAHMİNİ
    try:
        tx["gas"] = w3.eth.estimate_gas(tx)
    except:
        tx["gas"] = 300000

    # İMZALA
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

    # 🚀 **DOĞRU ALAN → raw_transaction**
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print("📨 TX gönderildi:", w3.to_hex(tx_hash))

    # ONAY BEKLE
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status == 1:
        print("✅ MINT BAŞARILI!")
    else:
        print("❌ MINT BAŞARISIZ!")

    return receipt


# =========================================================
#                PROGRAMI ÇALIŞTIR
# =========================================================
try:
    r = mint(ALICI_ADRES)

    if r:
        total = contract.functions.toplamKartSayisi().call()
        print("📌 Toplam Kart:", total)

        owner = contract.functions.kartSahibi(total).call()
        print("🆕 Son Kart Sahibi:", owner)

except Exception as e:
    print("❌ Genel Hata:", e)
