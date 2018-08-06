from django.db import models

# Create your models here.
class Folder(models.Model):
	name = models.CharField(max_length = 19)

	def __str__(self):
		return self.name

class mvolFolder(Folder):
	date = models.DateTimeField(null = True)
	valid = models.NullBooleanField(null = True)
	dev = models.DateTimeField(null = True)
	pro = models.DateTimeField(null = True)
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null = True, related_name = 'children')