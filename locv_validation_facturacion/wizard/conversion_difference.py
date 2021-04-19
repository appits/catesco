# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class ConversionDifference(models.TransientModel):
    _name = 'conversion.difference'

    invoice_id = fields.Many2one('account.move', string='Factura')
    date = fields.Date('Fecha Contable')
    ref = fields.Char('Referencia')
    journal_id = fields.Many2one('account.journal', string='Diario')
    account_id = fields.Many2one('account.account', string='Cuenta Contrapartida')

    def post(self):
        self.ensure_one()
        
        aml_obj = self.env['account.move.line']
        move= self.env['account.move'].create({
            'ref': self.ref,
            'date': self.date,
            'journal_id': self.journal_id.id
        })

        debit_line, credit_line = self._prepare_move_line_vals()
        debit_line['move_id'] = move.id
        credit_line['move_id'] = move.id
        
        print('####################')
        print(debit_line)
        print(credit_line)
        print('############################')
        aml_obj.create([debit_line, credit_line])
        
        #credit = aml_obj.create(credit_line)
        #(debit + credit).write({'move_id': move.id})
        move.post()
        return True
        

    

    def _prepare_move_line_vals(self):
        values = []
        
        invoice = self.invoice_id
        partner = invoice.partner_id

        if invoice.type == 'in_invoice':
            values.append({
                'account_id': partner.property_account_payable_id.id,
                'partner_id': partner.id,
                'debit': invoice.amount_residual,
            })

            values.append({
                'account_id': self.account_id.id,
                'partner_id': partner.id,
                'credit': invoice.amount_residual,
            })
        elif invoice.type == 'out_invoice':
            values.append({
                'account_id': self.account_id.id,
                'partner_id': partner.id,
                'debit': invoice.amount_residual,
            })

            values.append({
                'account_id': partner.property_account_receivable_id.id,
                'partner_id': partner.id,
                'credit': invoice.amount_residual,
            })
        else:
            raise UserError('Documento Invalido.')


        return values
