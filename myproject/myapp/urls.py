from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from myapp import views  # เพิ่มบรรทัดนี้เพื่อนำเข้า views จาก myapp

urlpatterns = [
    # เส้นทางเดิม
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),  # แก้ไขส่วนนี้จากความเห็นเป็นโค้ดจริง

    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('subscriptions/', views.SubscriptionPlanListView.as_view(), name='subscription_list'),
    path('subscriptions/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('subscriptions/<int:plan_id>/subscribe/', views.subscribe, name='subscribe'),
    path('my-subscriptions/', views.UserSubscriptionListView.as_view(), name='user_subscriptions'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
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

    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='myapp/password_change.html', 
        success_url='/dashboard/'), name='password_change'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('support/', views.support, name='support'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)