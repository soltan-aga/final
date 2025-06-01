from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import Category, Unit, Product, ProductUnit
from .forms import CategoryForm, UnitForm, ProductForm, ProductUnitFormSet
from users.decorators import can_create, can_edit, can_delete

# Category Views
@login_required
def category_list(request):
    """View to display all categories"""
    categories = Category.objects.all()
    return render(request, 'products/category/list.html', {'categories': categories})

@login_required
def category_detail(request, pk):
    """View to display category details"""
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()
    subcategories = category.children.all()
    return render(request, 'products/category/detail.html', {
        'category': category,
        'products': products,
        'subcategories': subcategories
    })

@login_required
def category_add(request):
    """View to add a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم إضافة القسم {category.name} بنجاح')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'products/category/form.html', {
        'form': form,
        'title': 'إضافة قسم جديد'
    })

@login_required
def category_edit(request, pk):
    """View to edit a category"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم تعديل القسم {category.name} بنجاح')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'products/category/form.html', {
        'form': form,
        'title': f'تعديل القسم {category.name}',
        'category': category
    })

@login_required
def category_delete(request, pk):
    """View to delete a category"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'تم حذف القسم {category_name} بنجاح')
        return redirect('category_list')

    return render(request, 'products/category/delete.html', {'category': category})

# Unit Views
@login_required
def unit_list(request):
    """View to display all units"""
    units = Unit.objects.all()
    return render(request, 'products/unit/list.html', {'units': units})

@login_required
def unit_add(request):
    """View to add a new unit"""
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'تم إضافة الوحدة {unit.name} بنجاح')
            return redirect('unit_list')
    else:
        form = UnitForm()

    return render(request, 'products/unit/form.html', {
        'form': form,
        'title': 'إضافة وحدة جديدة'
    })

@login_required
def unit_edit(request, pk):
    """View to edit a unit"""
    unit = get_object_or_404(Unit, pk=pk)

    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'تم تعديل الوحدة {unit.name} بنجاح')
            return redirect('unit_list')
    else:
        form = UnitForm(instance=unit)

    return render(request, 'products/unit/form.html', {
        'form': form,
        'title': f'تعديل الوحدة {unit.name}',
        'unit': unit
    })

@login_required
def unit_delete(request, pk):
    """View to delete a unit"""
    unit = get_object_or_404(Unit, pk=pk)

    if request.method == 'POST':
        unit_name = unit.name
        unit.delete()
        messages.success(request, f'تم حذف الوحدة {unit_name} بنجاح')
        return redirect('unit_list')

    return render(request, 'products/unit/delete.html', {'unit': unit})

# Product Views
@login_required
def product_list(request):
    """View to display all products"""
    products = Product.objects.all().prefetch_related('units', 'units__unit')

    # إضافة معلومات وحدات الشراء والبيع الافتراضية لكل منتج
    for product in products:
        # البحث عن وحدة الشراء الافتراضية
        default_purchase_unit = product.units.filter(is_default_purchase=True).first()
        # البحث عن وحدة البيع الافتراضية
        default_sale_unit = product.units.filter(is_default_sale=True).first()

        # إضافة المعلومات إلى كائن المنتج
        product.default_purchase_unit = default_purchase_unit
        product.default_sale_unit = default_sale_unit

    return render(request, 'products/product/list.html', {'products': products})

@login_required
def product_detail(request, pk):
    """View to display product details"""
    product = get_object_or_404(Product, pk=pk)
    product_units = product.units.all()
    return render(request, 'products/product/detail.html', {
        'product': product,
        'product_units': product_units
    })

@login_required
@can_create('product')
def product_add(request):
    """View to add a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductUnitFormSet(request.POST, prefix='units')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = form.save()
                # Set current_balance to initial_balance when creating
                product.current_balance = product.initial_balance
                product.save()

                # Save product units
                formset.instance = product
                formset.save()

                # التحقق من وجود وحدة شراء افتراضية ووحدة بيع افتراضية
                # نحصل على جميع وحدات المنتج بعد الحفظ (بما في ذلك الوحدات التي لم تتغير)
                all_units = ProductUnit.objects.filter(product=product)

                has_default_purchase = any(unit.is_default_purchase for unit in all_units)
                has_default_sale = any(unit.is_default_sale for unit in all_units)

                # إذا لم يتم تحديد وحدة افتراضية، نقوم بتعيين الوحدة الأولى كافتراضية
                if all_units.exists() and not has_default_purchase:
                    first_unit = all_units.first()
                    first_unit.is_default_purchase = True
                    first_unit.save()

                if all_units.exists() and not has_default_sale:
                    first_unit = all_units.first()
                    first_unit.is_default_sale = True
                    first_unit.save()

                messages.success(request, f'تم إضافة المنتج {product.name} بنجاح')
                return redirect('product_list')
    else:
        form = ProductForm()
        formset = ProductUnitFormSet(prefix='units')

    return render(request, 'products/product/form.html', {
        'form': form,
        'formset': formset,
        'title': 'إضافة منتج جديد'
    })

@login_required
@can_edit('product')
def product_edit(request, pk):
    """View to edit a product"""
    product = get_object_or_404(Product, pk=pk)
    print(f"🔍 بدء تعديل المنتج: {product.name} (#{product.id})")
    print(f"📊 المخزن الافتراضي الحالي: {product.default_store.name if product.default_store else 'لا يوجد'}")

    if request.method == 'POST':
        print("📝 استلام طلب POST لتعديل المنتج")
        # طباعة البيانات المستلمة من النموذج
        print(f"📊 البيانات المستلمة: {request.POST}")

        # التحقق من وجود المخزن الافتراضي في البيانات المرسلة
        default_store_id = request.POST.get('default_store')
        print(f"📊 معرف المخزن الافتراضي المرسل: {default_store_id}")

        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductUnitFormSet(request.POST, instance=product, prefix='units')

        print(f"🔍 التحقق من صحة النموذج - form.is_valid(): {form.is_valid()}")
        if not form.is_valid():
            print(f"❌ أخطاء النموذج: {form.errors}")

        print(f"🔍 التحقق من صحة formset - formset.is_valid(): {formset.is_valid()}")
        if not formset.is_valid():
            print(f"❌ أخطاء الـ formset: {formset.errors}")
            # طباعة أخطاء النماذج الفردية في الـ formset
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    print(f"❌ أخطاء النموذج {i} في الـ formset: {form_errors}")

        if form.is_valid() and formset.is_valid():
            print("✅ النموذج والـ formset صالحان، بدء عملية الحفظ")
            try:
                with transaction.atomic():
                    # Save the old initial balance and default store
                    old_initial_balance = product.initial_balance
                    old_default_store = product.default_store
                    print(f"📊 الرصيد الافتتاحي القديم: {old_initial_balance}")
                    print(f"📊 المخزن الافتراضي القديم: {old_default_store.name if old_default_store else 'لا يوجد'}")

                    # حفظ النموذج مباشرة بدون commit=False لضمان حفظ جميع الحقول
                    product = form.save()

                    # التحقق من تغيير المخزن الافتراضي
                    # نستخدم القيمة المعالجة من النموذج مباشرة
                    print(f"📊 المخزن الافتراضي من النموذج: {form.cleaned_data.get('default_store')}")

                    # لا نحتاج إلى تعيين المخزن الافتراضي يدويًا لأن form.save() سيقوم بذلك
                    # ولكن نتحقق من القيمة للتأكد من أنها صحيحة
                    if form.cleaned_data.get('default_store') != old_default_store:
                        print(f"📝 تم تغيير المخزن الافتراضي من {old_default_store.name if old_default_store else 'لا يوجد'} إلى {form.cleaned_data.get('default_store').name if form.cleaned_data.get('default_store') else 'لا يوجد'}")

                    print(f"✅ تم إنشاء كائن المنتج (لم يتم الحفظ بعد): {product.name}")
                    print(f"📊 المخزن الافتراضي الجديد: {product.default_store.name if product.default_store else 'لا يوجد'}")

                    # Adjust current balance based on the change in initial balance
                    if old_initial_balance != product.initial_balance:
                        difference = product.initial_balance - old_initial_balance
                        product.current_balance += difference
                        print(f"📊 تعديل الرصيد الحالي: {product.current_balance} (تغيير بمقدار {difference})")
                        # حفظ التغييرات في الرصيد الحالي فقط
                        product.save(update_fields=['current_balance'])
                    print(f"✅ تم حفظ المنتج في قاعدة البيانات: {product.name} (#{product.id})")

                    # التحقق من حفظ المخزن الافتراضي
                    product_after_save = Product.objects.get(pk=product.pk)
                    print(f"📊 المخزن الافتراضي بعد الحفظ: {product_after_save.default_store.name if product_after_save.default_store else 'لا يوجد'}")

                    # Save product units
                    print("📝 بدء حفظ وحدات المنتج")
                    formset.instance = product  # التأكد من ربط الـ formset بالمنتج المحدث
                    formset.save()
                    print("✅ تم حفظ وحدات المنتج")

                    # التحقق من وجود وحدة شراء افتراضية ووحدة بيع افتراضية
                    # نحصل على جميع وحدات المنتج بعد الحفظ (بما في ذلك الوحدات التي لم تتغير)
                    all_units = ProductUnit.objects.filter(product=product)
                    print(f"📊 عدد وحدات المنتج بعد الحفظ: {all_units.count()}")

                    has_default_purchase = any(unit.is_default_purchase for unit in all_units)
                    has_default_sale = any(unit.is_default_sale for unit in all_units)
                    print(f"📊 هل يوجد وحدة شراء افتراضية: {has_default_purchase}")
                    print(f"📊 هل يوجد وحدة بيع افتراضية: {has_default_sale}")

                    # إذا لم يتم تحديد وحدة افتراضية، نقوم بتعيين الوحدة الأولى كافتراضية
                    if all_units.exists() and not has_default_purchase:
                        first_unit = all_units.first()
                        first_unit.is_default_purchase = True
                        first_unit.save()
                        print(f"✅ تم تعيين الوحدة {first_unit.unit.name} كوحدة شراء افتراضية")

                    if all_units.exists() and not has_default_sale:
                        first_unit = all_units.first()
                        first_unit.is_default_sale = True
                        first_unit.save()
                        print(f"✅ تم تعيين الوحدة {first_unit.unit.name} كوحدة بيع افتراضية")

                    print("✅ تمت عملية الحفظ بنجاح")
                    messages.success(request, f'تم تعديل المنتج {product.name} بنجاح')

                    # إعادة التوجيه إلى صفحة تفاصيل المنتج
                    print(f"📝 إعادة التوجيه إلى صفحة تفاصيل المنتج: {product.pk}")
                    return redirect('product_detail', pk=product.pk)
            except Exception as e:
                print(f"❌ حدث خطأ أثناء حفظ المنتج: {str(e)}")
                messages.error(request, f'حدث خطأ أثناء حفظ المنتج: {str(e)}')
    else:
        print("📝 عرض نموذج تعديل المنتج")
        form = ProductForm(instance=product)
        formset = ProductUnitFormSet(instance=product, prefix='units')

    return render(request, 'products/product/form.html', {
        'form': form,
        'formset': formset,
        'title': f'تعديل المنتج {product.name}',
        'product': product
    })

@login_required
@can_delete('product')
def product_delete(request, pk):
    """View to delete a product"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'تم حذف المنتج {product_name} بنجاح')
        return redirect('product_list')

    return render(request, 'products/product/delete.html', {'product': product})

# API Views
@login_required
def product_units_api(request, product_id):
    """API to get product units"""
    try:
        print(f"🔍 تم استلام طلب API لوحدات المنتج رقم: {product_id}")

        # التحقق من وجود المنتج
        product = get_object_or_404(Product, pk=product_id)
        print(f"✅ تم العثور على المنتج: {product.name} (#{product.id})")

        # جلب وحدات المنتج
        units = product.units.all()
        print(f"📊 عدد وحدات المنتج: {units.count()}")

        units_data = []

        # تجميع معلومات الوحدات
        for unit in units:
            unit_data = {
                'id': unit.id,
                'unit_name': unit.unit.name,
                'unit_symbol': unit.unit.symbol,
                'conversion_factor': unit.conversion_factor,
                'is_default_purchase': unit.is_default_purchase,
                'is_default_sale': unit.is_default_sale,
                'purchase_price': float(unit.purchase_price),
                'sale_price': float(unit.selling_price),
                'selling_price': float(unit.selling_price),
                'barcode': unit.barcode
            }
            units_data.append(unit_data)
            print(f"🏷️ إضافة وحدة: {unit.unit.name} - سعر البيع: {unit.selling_price}, سعر الشراء: {unit.purchase_price}")

        # إعادة البيانات كـ JSON
        print(f"✅ إرسال استجابة كاملة بـ {len(units_data)} وحدة للمنتج {product.name}")
        return JsonResponse(units_data, safe=False)

    except Exception as e:
        print(f"❌ خطأ في طلب API لوحدات المنتج {product_id}: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'message': f'حدث خطأ أثناء جلب وحدات المنتج رقم {product_id}'
        }, status=500)

@login_required
def product_info_api(request, product_id):
    """API to get product information including units and prices"""
    try:
        print(f"🔍 تم استلام طلب API للمنتج رقم: {product_id}")

        # التحقق من وجود المنتج
        product = get_object_or_404(Product, pk=product_id)
        print(f"✅ تم العثور على المنتج: {product.name} (#{product.id})")

        # جلب وحدات المنتج
        product_units = product.units.all()
        print(f"📊 عدد وحدات المنتج: {product_units.count()}")

        units_data = []

        # تجميع معلومات الوحدات
        for unit in product_units:
            unit_data = {
                'id': unit.id,
                'unit_name': unit.unit.name,
                'unit_symbol': unit.unit.symbol,
                'conversion_factor': unit.conversion_factor,
                'is_default_purchase': unit.is_default_purchase,
                'is_default_sale': unit.is_default_sale,
                'purchase_price': unit.purchase_price,
                'selling_price': unit.selling_price
            }
            units_data.append(unit_data)
            print(f"🏷️ إضافة وحدة: {unit.unit.name} - سعر البيع: {unit.selling_price}, سعر الشراء: {unit.purchase_price}")

        # تجميع معلومات المنتج
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'barcode': product.barcode,
            'category': product.category.name if product.category else None,
            'units': units_data
        }

        # إعادة البيانات كـ JSON
        print(f"✅ إرسال استجابة كاملة بـ {len(units_data)} وحدة للمنتج {product.name}")
        return JsonResponse(product_data)

    except Exception as e:
        print(f"❌ خطأ في طلب API للمنتج {product_id}: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'message': f'حدث خطأ أثناء جلب معلومات المنتج رقم {product_id}'
        }, status=500)
