// cepkarti_frontend/globals.d.ts (veya benzer bir tiplendirme dosyasına ekleyin)

// Metamask'ın enjekte ettiği Ethereum nesnesini tanımlar.
interface Window {
  ethereum?: any; // Basitçe 'any' olarak tanımlıyoruz ki, ethers.js onu tanıyabilsin.
}