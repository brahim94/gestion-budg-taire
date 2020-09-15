# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class BudgetBudget(models.Model):
    _inherit = "crossovered.budget"

    type_budget = fields.Selection([
        ('normal', 'Normal'),
        ('chb', 'CHB')], string='Type Budget')

    # @api.depends('crossovered_budget_line.planned_amount')
    def _budget_all(self):
        for order in self:
            planned_amount = engagement_som = 0.0
            for line in order.crossovered_budget_line:
                planned_amount += line.planned_amount
                engagement_som += line.engagement_som
            order.update({
                'budget_total': planned_amount,
                'engagement_total': engagement_som,
            })

    budget_total = fields.Float(string='Total Budget', store=False, readonly=True, compute='_budget_all', tracking=True)
    engagement_total = fields.Float(string='Total Engagement', store=False, readonly=True, compute='_budget_all', tracking=True)
    
    #@api.depends('engagement_total')
    def _credit_availb(self):
        for order in self:
            credit_available = 0.0
            for line in order.crossovered_budget_line:
                credit_available = line.engagement_total_id - line.planned_amount
            order.update({
                'credit_available': credit_available,
            })

    credit_available = fields.Float(compute='_credit_availb', string="crédit disponible", store=False)
    
    @api.constrains('crossovered_budget_line.planned_amount')
    def _check_credit(self):
        for order in self:
            for line in order.crossovered_budget_line:
                if line.planned_amount > line.credit_available_id:
                    raise ValidationError('le montant engagement saisit dépasse le crédit disponible')

class EngegementEngagement(models.Model):
    _inherit = "market.execution"

    budget_ids = fields.Many2one('crossovered.budget', 'Budget')
    #bdg_lines = fields.Many2one('crossovered.budget.lines', 'ligne budgétaire')
    
class CrossoveredBudgetLinesInherit(models.Model):
    _inherit = "crossovered.budget.lines"

    engagement_id = fields.Many2one('market.execution', 'N° Engegement')

    @api.onchange('engagement_id')
    def onchange_employee_id(self):
        self.engagement_som = self.engagement_id.engagement_amount

    engagement_som = fields.Float(string="Montant d'engagement", store=True)
    engagement_total_id = fields.Float(related='crossovered_budget_id.engagement_total', string="Engagement total")
    credit_available_id = fields.Float(related='crossovered_budget_id.credit_available', string="Crédit disponible")
    
    
