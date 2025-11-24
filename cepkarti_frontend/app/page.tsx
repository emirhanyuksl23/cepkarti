'use client'

import React, { useState, useEffect } from 'react';
import { BrowserProvider } from 'ethers';
import Head from 'next/head';

// ============================
// AYARLAR
// ============================
const CONTRACT_ADDRESS: string = '0x5f81bD4460FeC194417E10d2821d9Dee69B7Df00';
const FASTAPI_MINT_URL: string = "http://127.0.0.1:8000/card/mint";
const FASTAPI_TOTAL_URL: string = "http://127.0.0.1:8000/card/count";
const SEPOLIA_CHAIN_ID = BigInt(11155111);

const CONTRACT_ABI: any[] = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": false,
        "inputs": [
            { "indexed": false, "internalType": "uint256", "name": "kartId", "type": "uint256" },
            { "indexed": false, "internalType": "address", "name": "sahip", "type": "address" }
        ],
        "name": "KartBasildi",
        "type": "event"
    },
    {
        "inputs": [
            { "internalType": "address", "name": "_alici", "type": "address" }
        ],
        "name": "yeniKartBas",
        "outputs": [
            { "internalType": "uint256", "name": "", "type": "uint256" }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            { "internalType": "uint256", "name": "", "type": "uint256" }
        ],
        "name": "kartSahibi",
        "outputs": [
            { "internalType": "address", "name": "", "type": "address" }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "toplamKartSayisi",
        "outputs": [
            { "internalType": "uint256", "name": "", "type": "uint256" }
        ],
        "stateMutability": "view",
        "type": "function"
    }
];

// ============================
// TYPE DECLARE
// ============================
declare global {
    interface Window {
        ethereum?: any;
    }
}

export default function CepKartiFrontend() {
    const [cuzdanAdresi, setCuzdanAdresi] = useState<string>('');
    const [hataMesaji, setHataMesaji] = useState<string>('');
    const [toplamKart, setToplamKart] = useState<number | null>(null);
    const [sonucMesaji, setSonucMesaji] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);

    // ============================
    // Metamask Bağlan
    // ============================
    const cuzdanBaglan = async () => {
        setHataMesaji('');
        setSonucMesaji('');

        if (!window.ethereum) {
            setHataMesaji("Metamask kurulu değil.");
            return;
        }

        try {
            const provider = new BrowserProvider(window.ethereum);
            setIsLoading(true);

            const accounts = await provider.send("eth_requestAccounts", []);
            if (!accounts.length) {
                setHataMesaji("Cüzdan bağlantısı reddedildi.");
                return;
            }

            const chainId = await provider.getNetwork().then(n => n.chainId);
            if (chainId !== SEPOLIA_CHAIN_ID) {
                setHataMesaji("Lütfen AĞI Sepolia yap.");
                await window.ethereum.request({
                    method: "wallet_switchEthereumChain",
                    params: [{ chainId: "0xaa36a7" }],
                });
                // Ağ değişiminden sonra tekrar bağlan
                await cuzdanBaglan();
                return;
            }

            setCuzdanAdresi(accounts[0]);
            await veriyiOku();

        } catch (err: any) {
            setHataMesaji("Bağlantı hatası: " + err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // ============================
    // Backend: Toplam Kart Sayısı Oku
    // ============================
    const veriyiOku = async () => {
        try {
            const res = await fetch(FASTAPI_TOTAL_URL);
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Kart sayısı okunamadı.");
            }
            const data = await res.json();
            setToplamKart(Number(data.total)); // 🔥 Düzeltildi
        } catch (err: any) {
            setToplamKart(null);
            setHataMesaji("Veri Okuma Hatası: " + err.message);
        }
    };

    // ============================
    // Yeni Kart Bas (API POST)
    // ============================
    const yeniKartBas = async () => {
        if (!cuzdanAdresi) {
            setHataMesaji("Önce Metamask bağla.");
            return;
        }

        setIsLoading(true);
        setSonucMesaji("⏳ İşlem başlatılıyor...");

        try {
            const res = await fetch(FASTAPI_MINT_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ alici_adres: cuzdanAdresi }),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Kart basma isteği başarısız oldu.");

            setSonucMesaji("✅ Kart Basıldı! Tx: " + data.tx_hash.slice(0, 12) + "...");
            setTimeout(veriyiOku, 7000); // Blockchain gecikmesi için
        } catch (err: any) {
            setHataMesaji("Kart Basma Hatası: " + err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // ============================
    // Auto bağlanma
    // ============================
    useEffect(() => {
        if (window.ethereum) {
            cuzdanBaglan();
        }
    }, []);

    // ============================
    // JSX
    // ============================
    const buton = {
        padding: '10px 20px',
        marginRight: '10px',
        color: 'white',
        borderRadius: '5px',
        fontWeight: 'bold',
        cursor: 'pointer'
    };

    return (
        <div style={{ padding: "40px", maxWidth: "800px", margin: "0 auto" }}>
            <Head><title>Cep Kartı NFT UI</title></Head>

            <h1 style={{ color: "#007BFF" }}>💳 Cep Kartı Yönetimi (FastAPI + Next.js)</h1>

            <div style={{ marginTop: "20px", padding: "20px", border: "1px solid #ccc", borderRadius: "8px" }}>
                <p><strong>Cüzdan:</strong> {cuzdanAdresi ? "Bağlı: " + cuzdanAdresi.slice(0, 6) + "..." : "❌ Bağlı Değil"}</p>
                <p><strong>Toplam Kart:</strong> {toplamKart !== null ? toplamKart : "Yükleniyor..."}</p>
            </div>

            {hataMesaji && <p style={{ color: "red" }}>HATA: {hataMesaji}</p>}
            {sonucMesaji && <p style={{ color: "green" }}>{sonucMesaji}</p>}

            <button
                onClick={cuzdanBaglan}
                disabled={!!cuzdanAdresi || isLoading}
                style={{ ...buton, background: cuzdanAdresi ? "#888" : "#4CAF50" }}>
                {cuzdanAdresi ? "Cüzdan Bağlı" : "Metamask ile Bağlan"}
            </button>

            <button
                onClick={yeniKartBas}
                disabled={!cuzdanAdresi || isLoading}
                style={{ ...buton, background: "#007BFF" }}>
                Yeni Kart Bas (FastAPI)
            </button>
        </div>
    );
}
