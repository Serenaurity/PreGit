from django.urls import path
from . import views

# urls.py - เพิ่มเส้นทาง

urlpatterns = [
    # เส้นทางเดิม
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('subscriptions/', views.SubscriptionPlanListView.as_view(), name='subscription_list'),
    path('subscriptions/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('subscriptions/<int:plan_id>/subscribe/', views.subscribe, name='subscribe'),
    path('my-subscriptions/', views.UserSubscriptionListView.as_view(), name='user_subscriptions'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # เส้นทางใหม่
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('content/', views.content_list, name='content_list'),
    path('nutrition-plan/', views.nutrition_plan, name='nutrition_plan'),
    path('community/', views.community_forum, name='community_forum'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('progress/', views.track_progress, name='track_progress'),
    path('progress/add/', views.add_progress, name='add_progress'),

    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('exercise-plan/', views.exercise_plan, name='exercise_plan'),
    path('exercise-plan/view/', views.view_exercise_plan, name='view_exercise_plan'),
    path('exercise-plan/day/<int:day_id>/', views.view_workout_day, name='view_workout_day'),
    path('meal-plan/', views.meal_plan, name='meal_plan'),
    path('meal-plan/view/', views.view_meal_plan, name='view_meal_plan'),
    path('meal-plan/day/<int:meal_id>/', views.view_daily_meal, name='view_daily_meal'),
    path('recipe/<int:recipe_id>/', views.view_recipe, name='view_recipe'),
]