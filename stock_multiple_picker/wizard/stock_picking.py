# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2016- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.exceptions
from openerp.exceptions import except_orm, Warning, RedirectWarning,MissingError
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class stock_picking_wizard(models.TransientModel):
    _name = 'stock.picking.multiple'
    _description = 'Set Picking Employees'
    
    def _default_employee_id(self):
        hr = self.env['hr.employee'].search([('user_id', '=', self.env.uid if self.env.uid else '')])
        return [(6,0,[hr[0].id])] if len(hr) > 0 else None
    
    def _default_picking_id(self):
        picking_id = self._context.get('active_id')
        if not picking_id:
            picking_id = self._context.get('active_ids') and self._context.get('active_ids')[0]
        return picking_id
    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Picking Employee', default=_default_employee_id, required=True)
    picking_id = fields.Many2one('stock.picking', 'Stock Picking', default=_default_picking_id, required=True)
    force = fields.Boolean('Replace Current Picking Employee')

    @api.multi
    def set_picking_employee(self):
        if self.force or not self.picking_id.employee_id:
            self.picking_id.employee_id = self.employee_ids[0]
            picker_count = len(self.employee_ids)
            for idx,line in enumerate(self.picking_id.move_lines):
                line.employee_id = self.employee_ids[idx % picker_count]
        else:
            raise Warning(_('Picking Employee is already set.'))

