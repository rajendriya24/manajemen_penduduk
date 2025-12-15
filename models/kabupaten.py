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

    _sql_constraints = [
        ('kabupaten_kode_unique', 'unique(kode)', 'Kode Kabupaten/Kota harus unik!'),
        ('kabupaten_name_prov_unique', 'unique(name, provinsi_id)', 'Nama Kabupaten/Kota pada provinsi yang sama harus unik!'),
    ]

    @api.constrains('kode')
    def _check_kode(self):
        """
        Kode boleh kosong.
        Kalau diisi, boleh:
        - angka saja (1101)
        - angka + titik (11.01, 32.04, dst)
        """
        for rec in self:
            if not rec.kode:
                continue

            kode = (rec.kode or '').strip()

            allowed_chars = set("0123456789.")
            if not set(kode).issubset(allowed_chars):
                raise ValidationError(
                    _("Kode Kabupaten/Kota hanya boleh berisi angka dan titik (contoh: 11.01).")
                )

            if kode.startswith('.') or kode.endswith('.'):
                raise ValidationError(
                    _("Kode Kabupaten/Kota tidak boleh diawali atau diakhiri titik.")
                )

            if '..' in kode:
                raise ValidationError(
                    _("Kode Kabupaten/Kota tidak boleh mengandung dua titik berturut-turut.")
                )

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
        """
        Ini yang bikin import Many2one bisa pakai kode.
        Saat import kecamatan, kolom kabupaten_code berisi '11.01' akan dicari ke field kode juga.
        """
        args = args or []
        if name:
            domain = ['|', ('name', operator, name), ('kode', operator, name)]
            return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid, order=order)
        return self._search(args, limit=limit, access_rights_uid=name_get_uid, order=order)

    def name_get(self):
        res = []
        for rec in self:
            if rec.kode:
                res.append((rec.id, f"{rec.name} [{rec.kode}]"))
            else:
                res.append((rec.id, rec.name))
        return res

    def toggle_active(self):
        for rec in self:
            rec.active = not rec.active