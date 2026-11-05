# B2F MAP LIVE

Monitor pemain online dan server publik Roblox untuk:
- Mount Blossom Peak — `89188079951257`
- Sekolah Malam Club — `117969282373364`
- Our Flower Garden — `132699740251419`

## Setup GitHub
1. Buat repository GitHub bernama `B2F-MAP-LIVE`.
2. Upload semua isi folder proyek ini, termasuk `.github/workflows/monitor.yml`.
3. Buka **Settings → Secrets and variables → Actions → New repository secret**.
4. Buat secret bernama `DISCORD_WEBHOOK_URL`, lalu isi dengan URL Discord Webhook.
5. Buka tab **Actions**, pilih **B2F MAP LIVE**, lalu klik **Run workflow** untuk tes pertama.
6. Pastikan workflow berada di default branch dan repository mengizinkan workflow berjalan.

## Catatan
- Jangan menaruh URL webhook langsung di kode atau membagikannya ke orang lain.
- Bot mengedit pesan Discord yang sama setelah ID pesan tersimpan di `message_id.txt`.
- Jumlah pemain diambil dari statistik experience Roblox; jika gagal, script memakai jumlah pemain dari server yang terdaftar.
- Jumlah server adalah server publik yang berhasil dipantau dari endpoint Roblox, bukan jaminan seluruh server global. Server privat/VIP tidak termasuk.
- Script memindai maksimal 20 halaman server per map.
- Jadwal GitHub Actions berjalan setiap 5 menit dan bisa terlambat; bukan update real-time per detik.
