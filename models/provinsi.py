# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class Provinsi(models.Model):
    _name = 'penduduk.provinsi'
    _description = 'Master Provinsi'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(string='Nama Provinsi', required=True, index=True)
    kode = fields.Char(string='Kode Provinsi', index=True)
    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('provinsi_kode_unique', 'unique(kode)', 'Kode Provinsi harus unik!'),
        ('provinsi_name_unique', 'unique(name)', 'Nama Provinsi harus unik!'),
    ]

    @api.constrains('kode')
    def _check_kode(self):
        for rec in self:
            if not rec.kode:
                continue
            kode = (rec.kode or '').strip()
            if not kode.isdigit():
                raise ValidationError(_("Kode Provinsi harus berupa angka."))
            if len(kode) < 2 or len(kode) > 10:
                raise ValidationError(_("Panjang Kode Provinsi harus 2 sampai 10 digit."))

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

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100,
                     name_get_uid=None, order=None):
        """
        FIX Odoo 17: harus terima parameter `order`.
        Plus: biar import Many2one bisa match pakai KODE juga (mis: '11').
        """
        args = args or []
        domain = []

        if name:
            name = name.strip()
            # cari by name atau by kode
            domain = expression.OR([
                [('name', operator, name)],
                [('kode', operator, name)],
            ])

        recs = self.search(expression.AND([args, domain]), limit=limit, order=order)
        return recs.ids