# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016, OVH SAS
#
# This file is part of Cerberus-core.
#
# Cerberus-core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
    Defined PhishingWorkflow
"""

from datetime import datetime, timedelta

from django.conf import settings

from utils import utils
from worker import Logger
from worker.workflows.report.abstract import ReportWorkflowBase


class PhishingReportWorkflow(ReportWorkflowBase):
    """
        Phishing report workflow
    """
    def identify(self, report, ticket, is_trusted=False):
        """
            identify if the `abuse.models.Report` match this workflow.

            :param `abuse.models.Report` report: A Cerberus report instance
            :param `abuse.models.Ticket` ticket: A Cerberus ticket instance
            :param bool is_trusted: If the report is trusted
            :return: If the workflow match
            :rtype: bool
        """
        is_there_some_urls = report.reportItemRelatedReport.filter(itemType='URL').exists()

        # Phishing specific workflow
        if report.category.name.lower() == 'phishing' and is_there_some_urls:
            return True
        return False

    def apply(self, report, ticket, is_trusted=False, no_phishtocheck=False):
        """
            Apply specific workflow on given `abuse.models.Report`

            :param `abuse.models.Report` report: A Cerberus report instance
            :param `abuse.models.Ticket` ticket: A Cerberus ticket instance
            :param bool is_trusted: If the report is trusted
            :param bool no_phishtocheck: if the report does not need PhishToCheck
            :return: If the workflow is applied
            :rtype: bool
        """
        from worker import phishing

        is_there_some_urls = report.reportItemRelatedReport.filter(itemType='URL').exists()
        all_down = phishing.check_if_all_down(report=report)

        # Archived report immediatly
        if all_down:
            phishing.close_because_all_down(report=report)
            Logger.debug(unicode('All down phishing workflow applied'))
            return True

        if no_phishtocheck:
            # Just pass
            return True

        # All items are clearly phishing ?
        new_ticket = False
        if all((is_trusted, is_there_some_urls, are_all_items_phishing(report))):
            if not ticket:
                ticket = _create_ticket(report)
                new_ticket = True

            _attach_report_to_ticket(report, ticket, new_ticket)
            phishing.block_url_and_mail(ticket_id=ticket, report_id=report)
            Logger.debug(unicode('Clearly phishing workflow applied'))
            return True

        # Report has to be manually checked
        if not report.provider.apiKey:  # Means it is not a trusted phishing provider
            report.status = 'PhishToCheck'
            report.save()
            utils.push_notification({
                'type': 'new phishToCheck',
                'id': report.id,
                'message': 'New PhishToCheck report %d' % (report.id),
            })
            Logger.debug(unicode('PhishToCheck workflow applied'))
            return True
        else:
            if not ticket and is_trusted:  # Create ticket
                ticket = _create_ticket(report)
                new_ticket = True

            if ticket:
                _attach_report_to_ticket(report, ticket, new_ticket)
                if is_there_some_urls:  # Block urls
                    phishing.block_url_and_mail(ticket_id=ticket, report_id=report)

            Logger.debug(unicode('Trusted phishing provider workflow applied'))
            return True


def are_all_items_phishing(report):
    """
        Returns if all items for given report are clearly phishing items (based on 'ping_url' service)

        :param `abuse.models.Report` report: A Cerberus report instance
        :return: If all items are clearly phishing items
        :rtype: bool
    """
    from worker import database
    result = set()

    for item in report.reportItemRelatedReport.filter(itemType='URL'):
        is_phishing = database.get_item_status_phishing(item.id, last=1)
        for res in is_phishing:
            result.add(res)

    response = False
    if len(result) == 1 and True in result:
        response = True

    return response


def _create_ticket(report):

    from worker import database
    ticket = database.create_ticket(report.defendant, report.category, report.service, priority=report.provider.priority)
    utils.scheduler.enqueue_in(
        timedelta(seconds=settings.GENERAL_CONFIG['phishing']['wait']),
        'ticket.timeout',
        ticket_id=ticket.id,
        timeout=3600,
    )
    ticket_snooze = settings.GENERAL_CONFIG['phishing']['wait']
    ticket.previousStatus = ticket.status
    ticket.status = 'WaitingAnswer'
    ticket.snoozeDuration = ticket_snooze
    ticket.snoozeStart = datetime.now()
    ticket.save()
    return ticket


def _attach_report_to_ticket(report, ticket, new_ticket):

    from worker import database

    report.ticket = ticket
    report.status = 'Attached'
    report.save()
    database.log_action_on_ticket(
        ticket=ticket,
        action='attach_report',
        report=report,
        new_ticket=new_ticket
    )
    database.set_ticket_higher_priority(report.ticket)