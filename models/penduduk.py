# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Penduduk(models.Model):
    _name = 'penduduk.penduduk'
    _description = 'Data Penduduk'
    _order = 'nik, nama'
    _rec_name = 'nama'

    nik = fields.Char(string='NIK', required=True, index=True)
    nama = fields.Char(string='Nama Lengkap', required=True, index=True)

    tempat_lahir = fields.Char(string='Tempat Lahir')
    tanggal_lahir = fields.Date(string='Tanggal Lahir')

    jenis_kelamin = fields.Selection(
        [('L', 'Laki-laki'), ('P', 'Perempuan')],
        string='Jenis Kelamin'
    )

    gol_darah = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')],
        string='Gol. Darah'
    )

    alamat = fields.Char(string='Alamat')
    rt = fields.Char(string='RT', size=3)
    rw = fields.Char(string='RW', size=3)

    agama = fields.Selection([
        ('islam', 'Islam'),
        ('kristen', 'Kristen'),
        ('katolik', 'Katolik'),
        ('hindu', 'Hindu'),
        ('buddha', 'Buddha'),
        ('konghucu', 'Konghucu'),
        ('lain', 'Lainnya'),
    ], string='Agama')

    status_perkawinan = fields.Selection([
        ('belum_kawin', 'Belum Kawin'),
        ('kawin', 'Kawin'),
        ('cerai_hidup', 'Cerai Hidup'),
        ('cerai_mati', 'Cerai Mati'),
    ], string='Status Perkawinan')

    pekerjaan = fields.Char(string='Pekerjaan')
    kewarganegaraan = fields.Selection(
        [('wni', 'WNI'), ('wna', 'WNA')],
        string='Kewarganegaraan',
        default='wni'
    )

    provinsi_id = fields.Many2one(
        'penduduk.provinsi',
        string='Provinsi',
        required=True,
        ondelete='restrict',
        index=True
    )
    kabupaten_id = fields.Many2one(
        'penduduk.kabupaten',
        string='Kabupaten/Kota',
        required=True,
        ondelete='restrict',
        index=True,
        domain="[('provinsi_id','=',provinsi_id), ('active','=',True)]"
    )
    kecamatan_id = fields.Many2one(
        'penduduk.kecamatan',
        string='Kecamatan',
        required=True,
        ondelete='restrict',
        index=True,
        domain="[('kabupaten_id','=',kabupaten_id), ('active','=',True)]"
    )
    kelurahan_id = fields.Many2one(
        'penduduk.kelurahan',
        string='Kelurahan/Desa',
        required=True,
        ondelete='restrict',
        index=True,
        domain="[('kecamatan_id','=',kecamatan_id), ('active','=',True)]"
    )

    foto = fields.Image(string='Foto', max_width=1024, max_height=1024)

    # ✅ tanda tangan digital langsung (disimpan sebagai image base64)
    ttd = fields.Image(string='Tanda Tangan', max_width=600, max_height=300)
    ttd_nama = fields.Char(string='Nama Penandatangan')

    catatan = fields.Text(string='Catatan')
    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('penduduk_nik_unique', 'unique(nik)', 'NIK harus unik!'),
    ]

    @api.constrains('nik')
    def _check_nik(self):
        for rec in self:
            if not rec.nik:
                continue
            nik = (rec.nik or '').strip()
            if not nik.isdigit():
                raise ValidationError(_("NIK harus berupa angka."))
            if len(nik) != 16:
                raise ValidationError(_("NIK harus 16 digit."))

    @api.onchange('provinsi_id')
    def _onchange_provinsi_id(self):
        if self.kabupaten_id and self.kabupaten_id.provinsi_id != self.provinsi_id:
            self.kabupaten_id = False
        self.kecamatan_id = False
        self.kelurahan_id = False

    @api.onchange('kabupaten_id')
    def _onchange_kabupaten_id(self):
        if self.kecamatan_id and self.kecamatan_id.kabupaten_id != self.kabupaten_id:
            self.kecamatan_id = False
        self.kelurahan_id = False

    @api.onchange('kecamatan_id')
    def _onchange_kecamatan_id(self):
        if self.kelurahan_id and self.kelurahan_id.kecamatan_id != self.kecamatan_id:
            self.kelurahan_id = False

    def toggle_active(self):
        for rec in self:
            rec.active = not rec.active