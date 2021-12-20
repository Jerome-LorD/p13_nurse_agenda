from django import template

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 



@register.simple_tag
def current_user(request):
	user_id = request.user.id
	return user_id