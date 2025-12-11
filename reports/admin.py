from django.contrib import admin
from .models import RoadFeedback, Comment

@admin.register(RoadFeedback)
class RoadFeedbackAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'road_name', 'user', 'issue_type', 'condition', 'city', 'state', 'created_at'
	)
	list_filter = ('condition', 'issue_type', 'state', 'city', 'created_at')
	search_fields = ('road_name', 'location', 'description', 'user__username')
	date_hierarchy = 'created_at'
	ordering = ('-created_at',)
	readonly_fields = ('latitude', 'longitude', 'created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('id', 'feedback', 'user', 'short_text', 'created_at')
	search_fields = ('text', 'user__username', 'feedback__road_name')
	list_filter = ('created_at',)
	ordering = ('-created_at',)

	def short_text(self, obj):
		return (obj.text[:50] + '…') if len(obj.text) > 50 else obj.text
	short_text.short_description = 'Comment'
