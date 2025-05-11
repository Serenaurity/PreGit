from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from .models import Product, SubscriptionPlan, Subscription, Order, OrderItem

# Home Page (FBV)
def home(request):
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    subscription_plans = SubscriptionPlan.objects.filter(is_active=True)
    context = {
        'featured_products': featured_products,
        'subscription_plans': subscription_plans
    }
    return render(request, 'myapp/home.html', context)

# Product List View
class ProductListView(ListView):
    model = Product
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True).order_by('-created_at')
        query = self.request.GET.get('q')  # Get the search term from the URL
        if query:
            # Filter products where name or description contains the query (case-insensitive)
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset

# Product Detail View
class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/product_detail.html'
    context_object_name = 'product'

# Subscription Plan List View
class SubscriptionPlanListView(ListView):
    model = SubscriptionPlan
    template_name = 'myapp/subscription_list.html'
    context_object_name = 'subscription_plans'
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

# Subscription Detail View
class SubscriptionDetailView(DetailView):
    model = SubscriptionPlan
    template_name = 'myapp/subscription_detail.html'
    context_object_name = 'subscription_plan'

# User's Subscription View
class UserSubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'myapp/user_subscription_list.html'
    context_object_name = 'subscriptions'
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

# Add to Cart (FBV)
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create order with 'pending' status (cart)
    order, created = Order.objects.get_or_create(
        user=request.user,
        status='pending'
    )
    
    # If order was just created, set initial total_amount
    if created:
        order.total_amount = 0
        order.save()
    
    # Check if item already in cart, if so increase quantity
    try:
        order_item = OrderItem.objects.get(order=order, product=product)
        order_item.quantity += 1
        order_item.save()
    except OrderItem.DoesNotExist:
        # Create new order item
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
    
    # Update order total
    order.total_amount = sum(item.price * item.quantity for item in order.items.all())
    order.save()
    
    return redirect('cart')

# View Cart (FBV)
@login_required
def view_cart(request):
    try:
        cart = Order.objects.get(user=request.user, status='pending')
        items = cart.items.all()
    except Order.DoesNotExist:
        cart = None
        items = []
    
    context = {
        'cart': cart,
        'items': items
    }
    return render(request, 'myapp/cart.html', context)

# Subscribe to plan (FBV)
@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Check if user already has an active subscription to this plan
    existing_subscription = Subscription.objects.filter(
        user=request.user,
        plan=plan,
        status='active'
    ).first()
    
    if existing_subscription:
        # Redirect to existing subscription
        return redirect('user_subscriptions')
    
    # Create new subscription (payment would be handled here in production)
    subscription = Subscription.objects.create(
        user=request.user,
        plan=plan
    )
    
    return redirect('user_subscriptions')

# views.py - เพิ่มฟังก์ชันวิว

# views.py
# แทนที่ของเดิมหรือแก้ไขเพิ่มเติม
@login_required
def user_dashboard(request):
    """หน้าแดชบอร์ดผู้ใช้"""
    # ดึงข้อมูลโปรไฟล์
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    # ดึงข้อมูลสมาชิก
    active_subscription = Subscription.objects.filter(
        user=request.user, 
        status='active', 
        end_date__gte=timezone.now().date()
    ).first()
    
    if active_subscription:
        # คำนวณจำนวนวันที่เหลือ
        remaining_days = (active_subscription.end_date - timezone.now().date()).days
        active_subscription.remaining_days = max(0, remaining_days)
    
    # ดึงข้อมูลออเดอร์ล่าสุด
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # ดึงข้อมูลแผนออกกำลังกาย
    exercise_plan = ExercisePlan.objects.filter(user=request.user).order_by('-created_at').first()
    
    # ดึงข้อมูลการออกกำลังกายวันนี้
    today_workout = None
    if exercise_plan:
        # หาวันในสัปดาห์ (1-7)
        today_weekday = timezone.now().weekday() + 1  # +1 เพราะ weekday() เริ่มที่ 0 (จันทร์)
        today_workout = WorkoutDay.objects.filter(
            exercise_plan=exercise_plan,
            day_number=today_weekday
        ).first()
    
    # ดึงข้อมูลแผนอาหาร
    meal_plan = MealPlan.objects.filter(user=request.user).order_by('-created_at').first()
    
    # ดึงข้อมูลอาหารวันนี้
    today_meal = None
    if meal_plan:
        # หาวันในสัปดาห์ (1-7)
        today_weekday = timezone.now().weekday() + 1  # +1 เพราะ weekday() เริ่มที่ 0 (จันทร์)
        today_meal = DailyMeal.objects.filter(
            meal_plan=meal_plan,
            day_number=today_weekday
        ).first()
    
    # ดึงบทความแนะนำ
    if user_profile and exercise_plan:
        # แนะนำบทความตามเป้าหมายการออกกำลังกาย
        goal_category = {
            'weight_loss': 'weight_loss',
            'fat_loss': 'weight_loss',
            'muscle_gain': 'muscle_building',
            'endurance': 'cardio',
            'general_fitness': 'general'
        }.get(exercise_plan.goal, 'general')
        
        recommended_articles = Content.objects.filter(
            category=goal_category,
            is_published=True
        ).order_by('-published_at')[:3]
    else:
        # แนะนำบทความทั่วไป
        recommended_articles = Content.objects.filter(
            is_published=True
        ).order_by('-published_at')[:3]
    
    # กิจกรรมล่าสุด
    last_activity = None
    if recent_orders.exists():
        last_activity = f"สั่งซื้อรายการ #{recent_orders[0].order_number} เมื่อ {recent_orders[0].created_at.strftime('%d/%m/%Y')}"
    elif exercise_plan:
        last_activity = f"สร้างแผนออกกำลังกายเมื่อ {exercise_plan.created_at.strftime('%d/%m/%Y')}"
    elif meal_plan:
        last_activity = f"สร้างแผนอาหารเมื่อ {meal_plan.created_at.strftime('%d/%m/%Y')}"
    
    context = {
        'user_profile': user_profile,
        'active_subscription': active_subscription,
        'recent_orders': recent_orders,
        'exercise_plan': exercise_plan,
        'today_workout': today_workout,
        'meal_plan': meal_plan,
        'today_meal': today_meal,
        'recommended_articles': recommended_articles,
        'last_activity': last_activity
    }
    return render(request, 'myapp/dashboard.html', context)

# หน้าบทความและวิดีโอ
def content_list(request):
    articles = Article.objects.filter(published=True).order_by('-date')
    videos = Video.objects.filter(published=True).order_by('-date')
    category = request.GET.get('category', None)
    
    if category:
        articles = articles.filter(category=category)
        videos = videos.filter(category=category)
    
    context = {
        'articles': articles,
        'videos': videos,
        'category': category,
    }
    return render(request, 'myapp/content_list.html', context)

# หน้าแผนโภชนาการ
@login_required
def nutrition_plan(request):
    user = request.user
    subscription = Subscription.objects.filter(user=user, status='active').first()
    
    if not subscription:
        return redirect('subscription_list')
    
    # รับหรือสร้างแผนโภชนาการเฉพาะบุคคล
    nutrition_plan, created = NutritionPlan.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = NutritionPreferencesForm(request.POST, instance=nutrition_plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกข้อมูลโภชนาการเรียบร้อยแล้ว')
    else:
        form = NutritionPreferencesForm(instance=nutrition_plan)
    
    context = {
        'nutrition_plan': nutrition_plan,
        'form': form,
    }
    return render(request, 'myapp/nutrition_plan.html', context)

# หน้าชุมชนและฟอรั่ม
@login_required
def community_forum(request):
    topics = ForumTopic.objects.all().order_by('-last_activity')
    popular_threads = ForumThread.objects.annotate(reply_count=Count('replies')).order_by('-reply_count')[:5]
    
    context = {
        'topics': topics,
        'popular_threads': popular_threads,
    }
    return render(request, 'myapp/community_forum.html', context)

# views.py - เพิ่มฟังก์ชันวิวสำหรับแผนออกกำลังกายและโภชนาการ

@login_required
def profile_setup(request):
    """หน้าตั้งค่าข้อมูลส่วนตัวสำหรับใช้ในแผน"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.has_completed_profile = True
            profile.save()
            messages.success(request, 'บันทึกข้อมูลส่วนตัวเรียบร้อยแล้ว')
            
            # ตรวจสอบว่ามาจากหน้าไหนแล้วเปลี่ยนเส้นทางการ redirect
            next_page = request.POST.get('next', 'dashboard')
            return redirect(next_page)
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'next': request.GET.get('next', 'dashboard')
    }
    return render(request, 'myapp/profile_setup.html', context)

@login_required
def exercise_plan(request):
    """หน้าจัดการแผนออกกำลังกาย"""
    # ตรวจสอบว่าผู้ใช้มีการสมัครสมาชิกที่ใช้งานอยู่
    active_subscription = Subscription.objects.filter(user=request.user, status='active').first()
    if not active_subscription:
        return redirect('subscription_list')
    
    # ตรวจสอบว่าผู้ใช้ได้กรอกข้อมูลส่วนตัวแล้วหรือไม่
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.has_completed_profile:
            messages.warning(request, 'โปรดกรอกข้อมูลส่วนตัวก่อนเพื่อสร้างแผนออกกำลังกาย')
            return redirect('profile_setup')
    except UserProfile.DoesNotExist:
        messages.warning(request, 'โปรดกรอกข้อมูลส่วนตัวก่อนเพื่อสร้างแผนออกกำลังกาย')
        return redirect('profile_setup')
    
    # ดึงแผนออกกำลังกายล่าสุดของผู้ใช้
    exercise_plan = ExercisePlan.objects.filter(user=request.user).order_by('-created_at').first()
    
    if request.method == 'POST':
        # สร้างหรือแก้ไขแผนออกกำลังกาย
        form = ExercisePlanForm(request.POST, instance=exercise_plan)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            
            # สร้างแผนการออกกำลังกายรายวัน
            generate_workout_plan(plan)
            
            messages.success(request, 'สร้างแผนออกกำลังกายเรียบร้อยแล้ว')
            return redirect('view_exercise_plan')
    else:
        form = ExercisePlanForm(instance=exercise_plan)
    
    context = {
        'form': form,
        'exercise_plan': exercise_plan
    }
    return render(request, 'myapp/exercise_plan_setup.html', context)

@login_required
def view_exercise_plan(request):
    """หน้าดูแผนออกกำลังกาย"""
    # ตรวจสอบว่าผู้ใช้มีการสมัครสมาชิกที่ใช้งานอยู่
    active_subscription = Subscription.objects.filter(user=request.user, status='active').first()
    if not active_subscription:
        return redirect('subscription_list')
    
    # ดึงแผนออกกำลังกายล่าสุดของผู้ใช้
    exercise_plan = ExercisePlan.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not exercise_plan:
        messages.info(request, 'คุณยังไม่มีแผนออกกำลังกาย กรุณาสร้างแผนใหม่')
        return redirect('exercise_plan')
    
    # ดึงแผนการออกกำลังกายรายวัน
    workout_days = WorkoutDay.objects.filter(exercise_plan=exercise_plan).prefetch_related('exercises__exercise')
    
    # จัดการแสดงผลปฏิทิน
    today = timezone.now().date()
    start_date = exercise_plan.start_date
    
    # สร้างปฏิทิน 4 สัปดาห์ (28 วัน)
    calendar_days = []
    for i in range(28):
        day_date = start_date + timezone.timedelta(days=i)
        day_number = i % 7 + 1  # วันที่ 1-7 ในแต่ละสัปดาห์
        
        # หาแผนการออกกำลังกายสำหรับวันนี้
        workout_day = next((day for day in workout_days if day.day_number == day_number), None)
        
        calendar_days.append({
            'date': day_date,
            'is_today': day_date == today,
            'is_past': day_date < today,
            'workout_day': workout_day,
            'week_number': i // 7 + 1
        })
    
    context = {
        'exercise_plan': exercise_plan,
        'workout_days': workout_days,
        'calendar_days': calendar_days
    }
    return render(request, 'myapp/view_exercise_plan.html', context)

@login_required
def view_workout_day(request, day_id):
    """หน้าดูรายละเอียดการออกกำลังกายรายวัน"""
    workout_day = get_object_or_404(WorkoutDay, id=day_id)
    
    # ตรวจสอบว่าเป็นแผนของผู้ใช้นี้
    if workout_day.exercise_plan.user != request.user:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงแผนนี้')
        return redirect('dashboard')
    
    # ดึงรายการออกกำลังกาย
    workout_exercises = WorkoutExercise.objects.filter(workout_day=workout_day).select_related('exercise')
    
    context = {
        'workout_day': workout_day,
        'workout_exercises': workout_exercises
    }
    return render(request, 'myapp/view_workout_day.html', context)

@login_required
def meal_plan(request):
    """หน้าจัดการแผนอาหาร"""
    # ตรวจสอบว่าผู้ใช้มีการสมัครสมาชิกที่ใช้งานอยู่
    active_subscription = Subscription.objects.filter(user=request.user, status='active').first()
    if not active_subscription:
        return redirect('subscription_list')
    
    # ตรวจสอบว่าผู้ใช้ได้กรอกข้อมูลส่วนตัวแล้วหรือไม่
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.has_completed_profile:
            messages.warning(request, 'โปรดกรอกข้อมูลส่วนตัวก่อนเพื่อสร้างแผนอาหาร')
            return redirect('profile_setup')
    except UserProfile.DoesNotExist:
        messages.warning(request, 'โปรดกรอกข้อมูลส่วนตัวก่อนเพื่อสร้างแผนอาหาร')
        return redirect('profile_setup')
    
    # ดึงแผนอาหารล่าสุดของผู้ใช้
    meal_plan = MealPlan.objects.filter(user=request.user).order_by('-created_at').first()
    
    # คำนวณพลังงานที่ร่างกายใช้ทั้งหมดในแต่ละวัน (TDEE)
    tdee = profile.calculate_tdee()
    
    if request.method == 'POST':
        # สร้างหรือแก้ไขแผนอาหาร
        form = MealPlanForm(request.POST, instance=meal_plan)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            
            # สร้างแผนอาหารรายวัน
            generate_meal_plan(plan)
            
            messages.success(request, 'สร้างแผนอาหารเรียบร้อยแล้ว')
            return redirect('view_meal_plan')
    else:
        # ถ้าไม่มีแผนอาหารเดิม ใช้ค่า TDEE เป็นค่าเริ่มต้น
        initial_data = {}
        if not meal_plan and tdee:
            goal = request.GET.get('goal', 'general_health')
            
            # ปรับค่าแคลอรี่ตามเป้าหมาย
            if goal == 'weight_loss':
                calories = max(1200, int(tdee * 0.8))  # ลด 20%
            elif goal == 'muscle_gain':
                calories = int(tdee * 1.1)  # เพิ่ม 10%
            else:
                calories = tdee
                
            initial_data = {
                'goal': goal,
                'daily_calories': calories
            }
            
        form = MealPlanForm(instance=meal_plan, initial=initial_data)
    
    context = {
        'form': form,
        'meal_plan': meal_plan,
        'tdee': tdee
    }
    return render(request, 'myapp/meal_plan_setup.html', context)

@login_required
def view_meal_plan(request):
    """หน้าดูแผนอาหาร"""
    # ตรวจสอบว่าผู้ใช้มีการสมัครสมาชิกที่ใช้งานอยู่
    active_subscription = Subscription.objects.filter(user=request.user, status='active').first()
    if not active_subscription:
        return redirect('subscription_list')
    
    # ดึงแผนอาหารล่าสุดของผู้ใช้
    meal_plan = MealPlan.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not meal_plan:
        messages.info(request, 'คุณยังไม่มีแผนอาหาร กรุณาสร้างแผนใหม่')
        return redirect('meal_plan')
    
    # ดึงแผนอาหารรายวัน
    daily_meals = DailyMeal.objects.filter(meal_plan=meal_plan).prefetch_related('meal_items__recipe')
    
    # คำนวณสารอาหารหลัก
    macros = meal_plan.calculate_macros()
    
    # จัดการแสดงผลปฏิทิน
    today = timezone.now().date()
    start_date = meal_plan.start_date
    
    # สร้างปฏิทิน 4 สัปดาห์ (28 วัน)
    calendar_days = []
    for i in range(28):
        day_date = start_date + timezone.timedelta(days=i)
        day_number = i % 7 + 1  # วันที่ 1-7 ในแต่ละสัปดาห์
        
        # หาแผนอาหารสำหรับวันนี้
        daily_meal = next((meal for meal in daily_meals if meal.day_number == day_number), None)
        
        calendar_days.append({
            'date': day_date,
            'is_today': day_date == today,
            'is_past': day_date < today,
            'daily_meal': daily_meal,
            'week_number': i // 7 + 1
        })
    
    context = {
        'meal_plan': meal_plan,
        'daily_meals': daily_meals,
        'calendar_days': calendar_days,
        'macros': macros
    }
    return render(request, 'myapp/view_meal_plan.html', context)

@login_required
def view_daily_meal(request, meal_id):
    """หน้าดูรายละเอียดอาหารรายวัน"""
    daily_meal = get_object_or_404(DailyMeal, id=meal_id)
    
    # ตรวจสอบว่าเป็นแผนของผู้ใช้นี้
    if daily_meal.meal_plan.user != request.user:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงแผนนี้')
        return redirect('user_dashboard')  # แก้ไขตามชื่อฟังก์ชันที่ถูกต้อง
    
    # ดึงรายการอาหาร
    meal_items = MealItem.objects.filter(daily_meal=daily_meal).select_related('recipe')
    
    # จัดกลุ่มตามมื้ออาหาร
    meals_by_time = {}
    for item in meal_items:
        if item.meal_time not in meals_by_time:
            meals_by_time[item.meal_time] = []
        meals_by_time[item.meal_time].append(item)
    
    # คำนวณค่าโภชนาการรวม
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    for item in meal_items:
        total_calories += item.recipe.calories_per_serving
        total_protein += item.recipe.protein
        total_carbs += item.recipe.carbs
        total_fat += item.recipe.fat
    
    # ปัดเศษทศนิยม
    total_protein = round(total_protein, 1)
    total_carbs = round(total_carbs, 1)
    total_fat = round(total_fat, 1)
    
    context = {
        'daily_meal': daily_meal,
        'meals_by_time': meals_by_time,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat
    }
    return render(request, 'myapp/view_daily_meal.html', context)

@login_required
def view_recipe(request, recipe_id):
   """หน้าดูรายละเอียดสูตรอาหาร"""
   recipe = get_object_or_404(Recipe, id=recipe_id)
   
   # ดึงส่วนผสม
   ingredients = Ingredient.objects.filter(recipe=recipe)
   
   context = {
       'recipe': recipe,
       'ingredients': ingredients
   }
   return render(request, 'myapp/view_recipe.html', context)

# ฟังก์ชั่นช่วยสร้างแผนออกกำลังกาย
def generate_workout_plan(exercise_plan):
   """สร้างแผนออกกำลังกายรายวันตามเป้าหมายและระดับความสามารถ"""
   # ลบแผนเดิมหากมี
   WorkoutDay.objects.filter(exercise_plan=exercise_plan).delete()
   
   # กำหนดวันออกกำลังกายตามจำนวนวันต่อสัปดาห์
   days_per_week = exercise_plan.days_per_week
   
   # สร้างแผนออกกำลังกายตามรูปแบบการฝึก
   if exercise_plan.training_focus == 'full_body':
       # แผนฝึกทั้งร่างกาย - กระจายวันฝึกให้ห่างกัน
       training_days = distribute_training_days(days_per_week)
       for day in range(1, 8):
           if day in training_days:
               workout_day = WorkoutDay.objects.create(
                   exercise_plan=exercise_plan,
                   day_number=day,
                   focus='full_body'
               )
               create_workout_exercises(workout_day, exercise_plan)
           else:
               WorkoutDay.objects.create(
                   exercise_plan=exercise_plan,
                   day_number=day,
                   focus='rest'
               )
   
   elif exercise_plan.training_focus == 'upper_lower':
       # แผนฝึกส่วนบน/ส่วนล่าง - สลับวันฝึก
       training_days = distribute_training_days(days_per_week)
       upper_lower_cycle = cycle(['upper_body', 'lower_body'])
       
       for day in range(1, 8):
           if day in training_days:
               focus = next(upper_lower_cycle)
               workout_day = WorkoutDay.objects.create(
                   exercise_plan=exercise_plan,
                   day_number=day,
                   focus=focus
               )
               create_workout_exercises(workout_day, exercise_plan)
           else:
               WorkoutDay.objects.create(
                   exercise_plan=exercise_plan,
                   day_number=day,
                   focus='rest'
               )
               
   elif exercise_plan.training_focus == 'push_pull_legs':
       # แผนฝึกแบบ Push/Pull/Legs
       training_days = distribute_training_days(min(6, days_per_week))  # สูงสุด 6 วัน
       ppl_cycle = cycle(['chest', 'back', 'legs'])  # Push, Pull, Legs
       
       for day in range(1, 8):
           if day in training_days:
               muscle_focus = next(ppl_cycle)
               # กำหนด focus สำหรับการแสดงผล
               if muscle_focus == 'chest':
                   display_focus = 'upper_body'  # Push
               elif muscle_focus == 'back':
                   display_focus = 'upper_body'  # Pull
               else:
                   display_focus = 'lower_body'  # Legs
               
               workout_day = WorkoutDay.objects.create(
                   exercise_plan=exercise_plan,
                   day_number=day,
                   focus=display_focus
               )
               create_workout_exercises(workout_day, exercise_plan, primary_muscle=muscle_focus)
           else:
               WorkoutDay.objects.create(
                   exercise_plan=exercise_plan,
                   day_number=day,
                   focus='rest'
               )

# ฟังก์ชั่นช่วยสร้างแผนอาหาร
def generate_meal_plan(meal_plan):
   """สร้างแผนอาหารรายวันตามเป้าหมายและความต้องการทางโภชนาการ"""
   # ลบแผนเดิมหากมี
   DailyMeal.objects.filter(meal_plan=meal_plan).delete()
   
   # สร้างชุดสูตรอาหารที่เหมาะสมตามเป้าหมาย
   diet_type = 'any'  # ค่าเริ่มต้น
   if 'vegetarian' in meal_plan.dietary_restrictions.lower():
       diet_type = 'vegetarian'
   elif 'vegan' in meal_plan.dietary_restrictions.lower():
       diet_type = 'vegan'
   
   # สร้างเมนูอาหารตามเป้าหมาย
   if meal_plan.goal == 'weight_loss':
       breakfast_recipes = Recipe.objects.filter(meal_type='breakfast', diet_type__in=[diet_type, 'any'], calories_per_serving__lt=400).order_by('?')
       lunch_recipes = Recipe.objects.filter(meal_type='lunch', diet_type__in=[diet_type, 'any'], calories_per_serving__lt=500).order_by('?')
       dinner_recipes = Recipe.objects.filter(meal_type='dinner', diet_type__in=[diet_type, 'any'], calories_per_serving__lt=500).order_by('?')
       snack_recipes = Recipe.objects.filter(meal_type='snack', diet_type__in=[diet_type, 'any'], calories_per_serving__lt=200).order_by('?')
   
   elif meal_plan.goal == 'muscle_gain':
       breakfast_recipes = Recipe.objects.filter(meal_type='breakfast', diet_type__in=[diet_type, 'any'], protein__gt=20).order_by('?')
       lunch_recipes = Recipe.objects.filter(meal_type='lunch', diet_type__in=[diet_type, 'any'], protein__gt=30).order_by('?')
       dinner_recipes = Recipe.objects.filter(meal_type='dinner', diet_type__in=[diet_type, 'any'], protein__gt=30).order_by('?')
       snack_recipes = Recipe.objects.filter(meal_type='snack', diet_type__in=[diet_type, 'any'], protein__gt=10).order_by('?')
   
   else:  # general_health, maintenance
       breakfast_recipes = Recipe.objects.filter(meal_type='breakfast', diet_type__in=[diet_type, 'any']).order_by('?')
       lunch_recipes = Recipe.objects.filter(meal_type='lunch', diet_type__in=[diet_type, 'any']).order_by('?')
       dinner_recipes = Recipe.objects.filter(meal_type='dinner', diet_type__in=[diet_type, 'any']).order_by('?')
       snack_recipes = Recipe.objects.filter(meal_type='snack', diet_type__in=[diet_type, 'any']).order_by('?')
   
   # หากไม่มีสูตรอาหารที่ตรงตามเงื่อนไข ใช้ทั้งหมด
   if not breakfast_recipes:
       breakfast_recipes = Recipe.objects.filter(meal_type='breakfast').order_by('?')
   if not lunch_recipes:
       lunch_recipes = Recipe.objects.filter(meal_type='lunch').order_by('?')
   if not dinner_recipes:
       dinner_recipes = Recipe.objects.filter(meal_type='dinner').order_by('?')
   if not snack_recipes:
       snack_recipes = Recipe.objects.filter(meal_type='snack').order_by('?')
   
   # สร้างแผนอาหาร 7 วัน
   for day in range(1, 8):
       daily_meal = DailyMeal.objects.create(
           meal_plan=meal_plan,
           day_number=day
       )
       
       # เพิ่มมื้ออาหาร
       # อาหารเช้า
       if breakfast_recipes:
           breakfast = breakfast_recipes[day % len(breakfast_recipes)]
           MealItem.objects.create(
               daily_meal=daily_meal,
               recipe=breakfast,
               meal_time='breakfast'
           )
       
       # อาหารกลางวัน
       if lunch_recipes:
           lunch = lunch_recipes[day % len(lunch_recipes)]
           MealItem.objects.create(
               daily_meal=daily_meal,
               recipe=lunch,
               meal_time='lunch'
           )
       
       # อาหารเย็น
       if dinner_recipes:
           dinner = dinner_recipes[day % len(dinner_recipes)]
           MealItem.objects.create(
               daily_meal=daily_meal,
               recipe=dinner,
               meal_time='dinner'
           )
       
       # อาหารว่าง (ถ้ามีมากกว่า 3 มื้อ)
       if meal_plan.meals_per_day > 3 and snack_recipes:
           snack = snack_recipes[day % len(snack_recipes)]
           MealItem.objects.create(
               daily_meal=daily_meal,
               recipe=snack,
               meal_time='snack'
           )

# views.py
# เพิ่มการนำเข้าฟังก์ชันช่วยเหลือ
from .utils import distribute_training_days, create_workout_exercises

# ใช้ในฟังก์ชัน generate_workout_plan
def generate_workout_plan(exercise_plan):
    """สร้างแผนออกกำลังกายรายวันตามเป้าหมายและระดับความสามารถ"""
    # ลบแผนเดิมหากมี
    WorkoutDay.objects.filter(exercise_plan=exercise_plan).delete()
    
    # กำหนดวันออกกำลังกายตามจำนวนวันต่อสัปดาห์
    days_per_week = exercise_plan.days_per_week
    
    # สร้างแผนออกกำลังกายตามรูปแบบการฝึก
    if exercise_plan.training_focus == 'full_body':
        # แผนฝึกทั้งร่างกาย - กระจายวันฝึกให้ห่างกัน
        training_days = distribute_training_days(days_per_week)
        for day in range(1, 8):
            if day in training_days:
                workout_day = WorkoutDay.objects.create(
                    exercise_plan=exercise_plan,
                    day_number=day,
                    focus='full_body'
                )
                create_workout_exercises(workout_day, exercise_plan)
            else:
                WorkoutDay.objects.create(
                    exercise_plan=exercise_plan,
                    day_number=day,
                    focus='rest'
                )
    
    elif exercise_plan.training_focus == 'upper_lower':
        # แผนฝึกส่วนบน/ส่วนล่าง - สลับวันฝึก
        training_days = distribute_training_days(days_per_week)
        upper_lower_cycle = cycle(['upper_body', 'lower_body'])
        
        for day in range(1, 8):
            if day in training_days:
                focus = next(upper_lower_cycle)
                workout_day = WorkoutDay.objects.create(
                    exercise_plan=exercise_plan,
                    day_number=day,
                    focus=focus
                )
                create_workout_exercises(workout_day, exercise_plan)
            else:
                WorkoutDay.objects.create(
                    exercise_plan=exercise_plan,
                    day_number=day,
                    focus='rest'
                )
                
    elif exercise_plan.training_focus == 'push_pull_legs':
        # แผนฝึกแบบ Push/Pull/Legs
        training_days = distribute_training_days(min(6, days_per_week))  # สูงสุด 6 วัน
        ppl_cycle = cycle(['chest', 'back', 'legs'])  # Push, Pull, Legs
        
        for day in range(1, 8):
            if day in training_days:
                muscle_focus = next(ppl_cycle)
                # กำหนด focus สำหรับการแสดงผล
                if muscle_focus == 'chest':
                    display_focus = 'upper_body'  # Push
                elif muscle_focus == 'back':
                    display_focus = 'upper_body'  # Pull
                else:
                    display_focus = 'lower_body'  # Legs
                
                workout_day = WorkoutDay.objects.create(
                    exercise_plan=exercise_plan,
                    day_number=day,
                    focus=display_focus
                )
                create_workout_exercises(workout_day, exercise_plan, primary_muscle=muscle_focus)
            else:
                WorkoutDay.objects.create(
                    exercise_plan=exercise_plan,
                    day_number=day,
                    focus='rest'
                )