#!/usr/bin/env python
# coding: utf-8

import os
from datetime import datetime

from assembla.api import API


api = API(
    key=os.getenv('ASSEMBLA_KEY'),
    secret=os.getenv('ASSEMBLA_SECRET')
)

aulasdovaca = api.spaces()[0]

api.space = aulasdovaca

milestones = api.milestones(space_id=aulasdovaca.id)

milestone = None
for ms in milestones:
    if ms.planner_type == 2:
        milestone = ms
        break

if milestone is None:
    raise TypeError('There is no default milestone!')

# burndown {
tickets = api.tickets(
    space_id=aulasdovaca.id,
    milestone_id=milestone.id
)

burndown_header = [
    '"Ticket number"',
    '"Completed date"',
    '"Sprint estimate"',
    '"Total working hours"',
    '"Team"',
    '"Assigned to"',
    '"Ticket extra"',
    '"Total estimate"',
    '"Finalizar no sprint"',
    '"Status"\n'
]

burndown_body = []
for ticket in tickets:
    assigned_to = '-'
    if ticket.assigned_to_id is not None:
        assigned_to = api.user(id=ticket.assigned_to_id).name.encode('ascii', 'ignore')

    burndown_body.append([
        str(ticket.number),
        str(ticket.completed_date or '-'),
        str(ticket.total_estimate),
        str(ticket.total_working_hours),
        '"%s"' % ticket.custom_fields['Equipe'],
        '"%s"' % assigned_to,
        '"%s"' % ticket.custom_fields['Ticket extra?'],
        '"%s"' % ticket.custom_fields.get('Estimativa total', '-'),
        '"%s"' % ticket.custom_fields['Finaliza no sprint?'],
        '"%s"\n' % ticket.status
    ])

# sorting by team
burndown_body.sort(key=lambda x: x[4])
# }


# tasks/worked hours {
tasks_header = [
    'Ticket',
    'User',
    'Worked hours',
    'Created at'
]

_from = milestone.created_at
to = datetime.now()

tasks = api.tasks(
    _from=_from.strftime('%d-%m-%Y'),
    to=to.strftime('%d-%m-%Y')
)

tasks_body = []

for task in tasks:
    ticket_number = '-'
    if task.ticket_id:
        ticket_number = api.ticket(space_id=aulasdovaca.id, id=task.ticket_id).number

    tasks_body.append([
        str(ticket_number),
        api.user(id=task.user_id).name.encode('ascii', 'ignore'),
        str(task.hours),
        str(task.created_at) + '\n'
    ])

# }

# writing file
with open('burndown.csv', 'w') as out:
    out.write(','.join(burndown_header))
    for line in burndown_body:
        out.write(','.join([l.encode('ascii', 'ignore') for l in line]))

    out.write('\n\n')

    out.write(','.join(tasks_header) + '\n')
    for line in tasks_body:
        out.write(','.join([l.encode('ascii', 'ignore') for l in line]))
