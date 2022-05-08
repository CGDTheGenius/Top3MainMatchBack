from django.db.models import Max

from board.models import Cell, Wall, Record


def construct_2d(entries):
    max_x = max(entry.x for entry in entries)
    max_y = max(entry.y for entry in entries)
    board = [[None for _ in range(max_y+1)] for __ in range(max_x+1)]
    for entry in entries:
        board[entry.x][entry.y] = entry
    return board


def construct_board():
    return construct_2d(Cell.objects.all())


def construct_horizontal_walls():
    return construct_2d(Wall.objects.filter(type='H_WALL'))


def construct_vertical_walls():
    return construct_2d(Wall.objects.filter(type='V_WALL'))


def not_movable(start, end, board, h_walls, v_walls, player, direction):
    sx, sy = start
    ex, ey = end
    cell = board[ex][ey]
    item = cell.items.first()

    # Allow backward approach for GREEN Artifact
    if direction == -1 and item and item.type == 'GREEN':
        return None

    # Wall
    if sx == ex:
        if not v_walls[ex][max(sy, ey)].fake and v_walls[ex][max(sy, ey)].closed:
            return '벽에 부딪혔습니다'
    else:
        if not h_walls[max(sx, ex)][ey].fake and h_walls[max(sx, ex)][ey].closed:
            return '벽에 부딪혔습니다'

    # Unavailable cell
    if cell.type not in ('BLANK', 'SAND', 'SOIL', 'GRASS', 'GRAVEL'):
        return '이동할 수 없는 지형에 부딪혔습니다'

    # Locked artifact
    if item and item.type not in player.unlocked:
        return '벽에 부딪혔습니다'

    return None


def create_player_record(player, task):
    return Record(
        player=player,
        turn=player.records.aggregate(Max('turn', default=0))['turn__max']+1,
        task=task,
        x=player.x,
        y=player.y,
        dx=player.dx,
        dy=player.dy,
        unlocked=player.unlocked,
        inventory=player.inventory,
    )


def create_assistant_record(assistant, task):
    return Record(
        assistant=assistant,
        turn=assistant.records.aggregate(Max('turn', default=0))['turn__max']+1,
        task=task,
    )


def extend_map(n, m):
    for i in range(n):
        for j in range(m):
            try:
                Cell(type='BLANK', x=i, y=j).save()
            except:
                pass
    for i in range(n+1):
        for j in range(m+1):
            try:
                Wall(type='H_WALL', x=i, y=j).save()
                Wall(type='V_WALL', x=i, y=j).save()
            except:
                pass
