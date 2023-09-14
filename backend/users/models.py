from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()

FOLLOW_STR = '{0} подписан на {1}'
SUBSCRIBE_ERROR = 'Нельзя подписаться на себя.'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Автор')

    class Meta:
        ordering = ('user', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='follow_user_author_constraint'),
        )

    def __str__(self) -> str:
        return FOLLOW_STR.format(
            self.user.get_username(), self.following.get_username())

    def clean(self):
        if self.user == self.following:
            raise ValidationError(SUBSCRIBE_ERROR)
