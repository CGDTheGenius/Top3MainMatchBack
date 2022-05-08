from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from board import unlocker
from board.models import Cell, Item, Player, Task, Wall, Assistant, Record
from board.serializers import CellSerializer, ItemSerializer, PlayerSerializer, TaskSerializer, BoardSerializer, \
    WallSerializer, AssistantSerializer, SightSerializer
from board.utils import construct_board, construct_horizontal_walls, construct_vertical_walls, not_movable, \
    create_player_record, create_assistant_record


class BoardView(generics.RetrieveAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self


class CellList(generics.ListAPIView):
    queryset = Cell.objects.all()
    serializer_class = CellSerializer


class CellDetail(generics.RetrieveUpdateAPIView):
    serializer_class = CellSerializer

    def get_object(self):
        cell = Cell.objects.filter(x=self.kwargs['x'], y=self.kwargs['y']).first()
        return cell


class WallDetail(generics.RetrieveUpdateAPIView):
    serializer_class = WallSerializer

    def get_object(self):
        wall = Wall.objects.filter(type=self.kwargs['type'], x=self.kwargs['x'], y=self.kwargs['y']).first()
        return wall


class ItemList(generics.ListCreateAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        return Item.objects.filter(cell__x=self.kwargs['x'], cell__y=self.kwargs['y'])

    def perform_create(self, serializer):
        cell = Cell.objects.filter(x=self.kwargs['x'], y=self.kwargs['y']).first()
        if cell.items.count() >= 3:
            cell.items.all().delete()
            raise ValidationError()
        if cell.items.count() > 0 and cell.items.first().type != self.request.data['type']:
            cell.items.all().delete()
        serializer.save(cell=cell)


class PlayerList(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAdminUser]


class PlayerDetail(generics.RetrieveAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Player.objects.get_by_natural_key(self.request.user.username)


class PlayerSight(generics.RetrieveAPIView):
    serializer_class = SightSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Player.objects.get_by_natural_key(self.request.user.username)


class AssistantList(generics.ListAPIView):
    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer
    permission_classes = [IsAdminUser]


class AssistantDetail(generics.RetrieveAPIView):
    serializer_class = AssistantSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Assistant.objects.get_by_natural_key(self.request.user.username)


class TaskList(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset):
        player = Player.objects.get_by_natural_key(self.request.user.username)
        return queryset.filter(player_id=player.id)


class RegisterTask(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            player = Player.objects.get_by_natural_key(self.request.user.username)
            player.tasks.filter(done=False).delete()
            serializer.save(player=player)
        except:
            assistant = Assistant.objects.get_by_natural_key(self.request.user.username)
            assistant.tasks.filter(done=False).delete()
            serializer.save(assistant=assistant)


class ProcessPlayerTask(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        board = construct_board()
        h_walls = construct_horizontal_walls()
        v_walls = construct_vertical_walls()

        for task in Task.objects.filter(done=False, player__isnull=False):
            player = task.player
            if task.type == 'MOVE':
                step = int(task.value)
                direction = 0 if step == 0 else step // abs(step)
                px, py = player.x, player.y
                for i in range(abs(step)):
                    nx, ny = px + player.dx * direction, py + player.dy * direction
                    if disable := not_movable((px, py), (nx, ny), board, h_walls, v_walls, player, direction):
                        # Move Fail
                        task.error = disable
                        break
                    px, py = nx, ny
                else:
                    # Move Success
                    player.move(step)
                    cell = board[player.x][player.y]
                    if item := cell.items.first():
                        # Warp trap
                        if item.type == 'FAKE':
                            task.error = '가짜 유물에 의해 워프당했습니다.'
                            player.x, player.y = 15, 15
                        # Acquire artifacts
                        if item.type in ('RED', 'BLUE', 'GREEN', 'YELLOW') and item.type not in player.inventory:
                            if item.type not in player.unlocked:
                                player.unlocked += '/'+item.type
                            player.inventory += '/'+item.type
                            item.delete()

            elif task.type == 'ROTATE':
                step = int(task.value)
                player.rotate(step)

            elif task.type == 'COMMUNICATE':
                is_tower_near = Cell.objects.filter(x__range=(player.x-1, player.x+1), y__range=(player.y-1, player.y+1), items__type='TOWER').exists()
                if is_tower_near:
                    new_task = Task(assistant=player.assistant, type='REVERSE_COMMUNICATE', value=task.value, done=True)
                    new_task.save()
                    create_assistant_record(new_task.assistant, new_task).save()
                else:
                    task.error = '통신탑이 근처에 없습니다'

            # Done Task
            task.done = True
            task.save()
            player.save()

            # Record
            record = create_player_record(player, task)
            record.save()

            # Try Unlock Artifacts
            unlocker.unlock(player, board)
        return Response()


class ProcessAssistantTask(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        for task in Task.objects.filter(done=False, assistant__isnull=False):
            task.done = True
            task.save()
            new_task = Task(player=task.assistant.partner, type='REVERSE_COMMUNICATE', value=task.value, done=True)
            new_task.save()
            create_player_record(new_task.player, new_task).save()

            # Record
            create_assistant_record(task.assistant, task).save()
        return Response()
