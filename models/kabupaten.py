# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Kabupaten(models.Model):
    _name = 'penduduk.kabupaten'
    _description = 'Master Kabupaten/Kota'
    _order = 'provinsi_id, name'
    _rec_name = 'name'

    name = fields.Char(string='Nama Kabupaten/Kota', required=True, index=True)
    kode = fields.Char(string='Kode Kabupaten/Kota', index=True)
    provinsi_id = fields.Many2one(
        'penduduk.provinsi',
        string='Provinsi',
        required=True,
        ondelete='restrict',
        index=True,
    )
    active = fields.Boolean(string='Aktif', default=True)

    # Optional tapi bagus untuk kualitas data
    _sql_constraints = [
        ('kabupaten_kode_unique', 'unique(kode)', 'Kode Kabupaten/Kota harus unik!'),
        ('kabupaten_name_prov_unique', 'unique(name, provinsi_id)', 'Nama Kabupaten/Kota pada provinsi yang sama harus unik!'),
    ]

    @api.constrains('kode')
    def _check_kode(self):
        """
        Kode boleh kosong.
        Kalau diisi, harus angka dan panjang 2-10 digit (bisa kamu sesuaikan).
        """
        for rec in self:
            if not rec.kode:
                continue
            kode = (rec.kode or '').strip()
            if not kode.isdigit():
                raise ValidationError(_("Kode Kabupaten/Kota harus berupa angka."))
            if len(kode) < 2 or len(kode) > 10:
                raise ValidationError(_("Panjang Kode Kabupaten/Kota harus 2 sampai 10 digit."))

    def name_get(self):
        """
        Tampilan nama yang enak di dropdown:
        'Kabupaten X [3204]'
        """
        res = []
        for rec in self:
            if rec.kode:
                res.append((rec.id, f"{rec.name} [{rec.kode}]"))
            else:
                res.append((rec.id, rec.name))
        return res

    def toggle_active(self):
        """
        Dipakai oleh tombol Arsipkan/Pulihkan di form view.
        """
        for rec in self:
            rec.active = not rec.active