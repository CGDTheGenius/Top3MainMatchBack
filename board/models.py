from django.db import models
from django.contrib.auth import models as auth_models


class Cell(models.Model):
    type = models.CharField(max_length=100)
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['x', 'y'],
                name='unique position',
            ),
        ]

    def __str__(self):
        return f'({self.x},{self.y})[{self.type}]'


class Wall(models.Model):
    type = models.CharField(max_length=100)
    x = models.IntegerField()
    y = models.IntegerField()
    closed = models.BooleanField(default=False)
    fake = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'x', 'y'],
                name='unique position and direction',
            ),
        ]

    def __str__(self):
        return f'({self.x},{self.y})[{self.type}{"_FAKE" if self.fake else ""}]'


class Item(models.Model):
    type = models.CharField(max_length=100)
    cell = models.ForeignKey(Cell, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.cell}[{self.type}]'


rotations = ((1, 0), (0, -1), (-1, 0), (0, 1))


class Player(auth_models.User):
    objects = auth_models.UserManager()

    color = models.CharField(max_length=100)
    dx = models.IntegerField(default=1)
    dy = models.IntegerField(default=0)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    unlocked = models.CharField(max_length=100, default='FAKE/TOWER', blank=True)
    inventory = models.CharField(max_length=100, default='TOWER', blank=True)

    def move(self, step):
        step = min(step, 10)
        self.x += self.dx * step
        self.y += self.dy * step

    def rotate(self, step):
        rotation_index = rotations.index((self.dx, self.dy))
        rotation_index += step
        while rotation_index < 0:
            rotation_index += len(rotations)
        while rotation_index >= len(rotations):
            rotation_index -= len(rotations)
        self.dx, self.dy = rotations[rotation_index]

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'


class Assistant(auth_models.User):
    objects = auth_models.UserManager()

    partner = models.OneToOneField(Player, related_name='assistant', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.username}'

    class Meta:
        verbose_name = 'Assistant'
        verbose_name_plural = 'Assistants'


class Task(models.Model):
    player = models.ForeignKey(Player, related_name='tasks', on_delete=models.CASCADE, null=True)
    assistant = models.ForeignKey(Assistant, related_name='tasks', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100)
    value = models.CharField(max_length=100, null=True, blank=True)
    done = models.BooleanField(default=False)
    error = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f'[{self.type}]{self.value} for {self.player if self.player else self.assistant}{["", " (DONE)"][self.done]}{" with " + self.error if self.error else ""}'


class Record(models.Model):
    player = models.ForeignKey(Player, related_name='records', on_delete=models.CASCADE, null=True)
    assistant = models.ForeignKey(Assistant, related_name='records', on_delete=models.CASCADE, null=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    turn = models.IntegerField()
    dx = models.IntegerField(null=True, blank=True)
    dy = models.IntegerField(null=True, blank=True)
    x = models.IntegerField(null=True, blank=True)
    y = models.IntegerField(null=True, blank=True)
    unlocked = models.CharField(max_length=100, null=True, blank=True)
    inventory = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.player if self.player else self.assistant} T{self.turn} ({self.x},{self.y})'
