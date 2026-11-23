# Dataset uji baru: satu fungsi pendek dan satu fungsi panjang.
# Label aktual akan dihitung otomatis dengan Pylint R0915.

def hitung_diskon(harga, pelanggan_baru):
    if pelanggan_baru:
        return harga * 0.9
    return harga


def proses_pesanan(pesanan, pelanggan, pengaturan, mata_uang, logger):
    if not pesanan:
        logger.warning("Pesanan kosong")
        return {"status": "ditolak"}

    total = 0
    for item in pesanan:
        if item["jumlah"] <= 0:
            logger.warning("Jumlah tidak valid")
            continue
        harga = item["harga"]
        if item.get("diskon"):
            harga = harga * (1 - item["diskon"])
        total += harga * item["jumlah"]

    if pelanggan.get("member"):
        total = total * 0.95
    if total > pengaturan["batas_gratis_ongkir"]:
        ongkir = 0
    else:
        ongkir = pengaturan["tarif_ongkir"]

    pajak = total * pengaturan["tarif_pajak"]
    if pelanggan.get("negara") != pengaturan["negara_toko"]:
        pajak = total * pengaturan["tarif_pajak_internasional"]
    elif pelanggan.get("bebas_pajak"):
        pajak = 0

    subtotal = 0
    for item in pesanan:
        subtotal += item["harga"] * item["jumlah"]
    if subtotal > 1000000:
        logger.warning("Pesanan bernilai tinggi")

    total_akhir = total + pajak + ongkir
    if total_akhir < 0:
        raise ValueError("Total tidak valid")

    status = "lunas" if pelanggan.get("prepaid") else "menunggu"
    if status == "menunggu" and total_akhir > 500000:
        status = "perlu_verifikasi"

    biaya_pemasaran = 0
    for item in pesanan:
        if item.get("kategori") == "promosi":
            biaya_pemasaran += item["harga"] * item["jumlah"] * 0.02
    if biaya_pemasaran > 250000:
        logger.warning("Biaya promosi pesanan tinggi")
    if ongkir > pengaturan["tarif_ongkir"]:
        logger.info("Pesanan menggunakan tarif kirim khusus")
    if pajak == 0:
        logger.info("Pesanan dibebaskan dari pajak")
    else:
        logger.info("Pajak pesanan diterapkan")

    total_akhir = round(total_akhir, 2)
    biaya_pemasaran = round(biaya_pemasaran, 2)
    hasil = {
        "status": status,
        "subtotal": subtotal,
        "pajak": pajak,
        "ongkir": ongkir,
        "total": total_akhir,
        "mata_uang": mata_uang,
        "biaya_pemasaran": biaya_pemasaran,
        "jumlah_item": len(pesanan),
        "id_pelanggan": pelanggan.get("id"),
    }
    hasil["total_dibulatkan"] = total_akhir
    logger.debug("Hasil pesanan telah dibentuk")
    logger.debug("Memeriksa hasil sebelum dikembalikan")
    logger.debug("Nilai total akhir telah dihitung")
    logger.debug("Ringkasan pelanggan tersedia")
    logger.debug("Ringkasan pesanan siap dikembalikan")
    logger.info("Pesanan selesai: %s", status)
    return hasil
