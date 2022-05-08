from board.models import Cell, rotations


def unlock_red(player, board, records):
    cells = Cell.objects.filter(x__range=(player.x-1, player.x+1), y__range=(player.y-1, player.y+1))
    for cell in cells:
        if cell.items.filter(type='RED').exists():
            if records.filter(x__in=(cell.x - 1, cell.x + 1), y__in=(cell.y - 1, cell.y + 1)).values('x', 'y').distinct().count() >= 4:
                player.unlocked += '/'+'RED'
                return


def unlock_blue(player, board, records):
    if records.count() < 2:
        return
    records = records.order_by('-turn')[:2]
    if records[0].task.type == 'COMMUNICATE' and records[0].task.value == '따랑해':
        if records[1].task.type == 'REVERSE_COMMUNICATE' and records[1].task.value == '따라해':
            player.unlocked += '/'+'BLUE'
            return


def unlock_yellow(player, board, records):
    if records.count() < 5:
        return
    records = records.order_by('-turn')[:5]
    last = records[0]
    if not any(
        Cell.objects.filter(x=(last.x+dx), y=(last.y+dy), items__type='YELLOW').exists()
        for dx, dy in rotations
    ):
        return
    last_dir = rotations.index((last.dx, last.dy))
    offset = None

    def get_offset(r):
        o = last_dir - rotations.index((r.dx, r.dy))
        if o == -3:
            o = 1
        elif o == 3:
            o = -1
        return o

    for record in records[1:]:
        if record.x != last.x or record.y != last.y:
            return
        if offset is None:
            offset = get_offset(record)
        elif offset != get_offset(record):
            return
        last_dir = rotations.index((record.dx, record.dy))
    player.unlocked += '/'+'YELLOW'
    return


def unlock(player, board):
    records = player.records.order_by('turn')
    last = records.last()
    if not last:
        return
    if 'RED' not in player.unlocked:
        unlock_red(player, board, records)
    if 'BLUE' not in player.unlocked:
        unlock_blue(player, board, records)
    if 'YELLOW' not in player.unlocked:
        unlock_yellow(player, board, records)
    player.save()
