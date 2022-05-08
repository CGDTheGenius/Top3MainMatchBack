from rest_framework import serializers

from board.models import Cell, Item, Player, Task, Wall, Assistant


class ItemSerializer(serializers.ModelSerializer):
    x = serializers.SerializerMethodField()
    y = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'type', 'cell', 'x', 'y']
        read_only_fields = ('cell', 'x', 'y')

    def get_x(self, obj):
        return obj.cell.x

    def get_y(self, obj):
        return obj.cell.y


class CellSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cell
        fields = ['id', 'type', 'x', 'y', 'items']


class WallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wall
        fields = ['id', 'type', 'x', 'y', 'closed', 'fake']


class BoardSerializer(serializers.Serializer):
    cells = serializers.SerializerMethodField()
    h_walls = serializers.SerializerMethodField()
    v_walls = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    def get_cells(self, obj):
        return CellSerializer(Cell.objects.all(), many=True).data

    def get_h_walls(self, obj):
        return WallSerializer(Wall.objects.filter(type='H_WALL'), many=True).data

    def get_v_walls(self, obj):
        return WallSerializer(Wall.objects.filter(type='V_WALL'), many=True).data

    def get_items(self, obj):
        return ItemSerializer(Item.objects.all(), many=True).data


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('done', 'player', 'assistant', 'error')


class PlayerSerializer(serializers.ModelSerializer):
    undone_task = serializers.SerializerMethodField()
    last_task = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['id', 'username', 'color', 'dx', 'dy', 'x', 'y', 'unlocked', 'inventory', 'last_task', 'undone_task']

    def get_undone_task(self, player):
        task = player.tasks.filter(done=False).order_by('id').last()
        return TaskSerializer(task, read_only=True).data if task else None

    def get_last_task(self, player):
        task = player.tasks.filter(done=True).order_by('id').last()
        return TaskSerializer(task, read_only=True).data if task else None


class PlayerSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'username', 'color', 'x', 'y']


class AssistantSerializer(serializers.ModelSerializer):
    undone_task = serializers.SerializerMethodField()
    last_task = serializers.SerializerMethodField()

    class Meta:
        model = Assistant
        fields = ['id', 'username', 'last_task', 'undone_task']

    def get_undone_task(self, player):
        task = player.tasks.filter(done=False).order_by('id').last()
        return TaskSerializer(task, read_only=True).data if task else None

    def get_last_task(self, player):
        task = player.tasks.filter(done=True).order_by('id').last()
        return TaskSerializer(task, read_only=True).data if task else None


class SightSerializer(serializers.Serializer):
    cells = serializers.SerializerMethodField()
    h_walls = serializers.SerializerMethodField()
    v_walls = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    others = serializers.SerializerMethodField()

    def get_cells(self, player):
        cells = Cell.objects.filter(x__range=(player.x-1, player.x+1), y__range=(player.y-1, player.y+1))
        return CellSerializer(cells, many=True).data

    def get_items(self, player):
        return ItemSerializer(Item.objects.all(), many=True).data

    def get_h_walls(self, player):
        walls = Wall.objects.filter(type='H_WALL', x__range=(player.x-1, player.x+2), y__range=(player.y-1, player.y+2))
        return WallSerializer(walls, many=True).data

    def get_v_walls(self, player):
        walls = Wall.objects.filter(type='V_WALL', x__range=(player.x-1, player.x+2), y__range=(player.y-1, player.y+2))
        return WallSerializer(walls, many=True).data

    def get_others(self, player):
        others = Player.objects\
            .exclude(id=player.id)\
            .filter(x__range=(player.x-1, player.x+1), y__range=(player.y-1, player.y+1))
        return PlayerSerializerSimple(others, many=True).data
