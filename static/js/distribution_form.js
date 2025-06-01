$(document).ready(function() {
    console.log('Distribution form JavaScript loaded');
    console.log('Current URL:', window.location.pathname);
    console.log('Distribution section exists:', $('#distribution-section').length);

    // متغيرات للتحكم في النماذج
    let formCount = parseInt($('#id_distribution_items-TOTAL_FORMS').val()) || 0;
    const maxForms = parseInt($('#id_distribution_items-MAX_NUM_FORMS').val()) || 1000;

    console.log('Initial formCount:', formCount);
    console.log('Max forms:', maxForms);

    // تحديث العداد بناءً على النماذج الموجودة
    const existingForms = $('.distribution-item').length;
    if (existingForms > 0) {
        formCount = existingForms;
        updateFormCount();
        console.log('Updated formCount based on existing forms:', formCount);
    }

    // تحديث عدد النماذج
    function updateFormCount() {
        $('#id_distribution_items-TOTAL_FORMS').val(formCount);
    }

    // إضافة عنصر توزيع جديد
    $('#add-item').click(function(e) {
        e.preventDefault();
        console.log('Add item button clicked!');

        // حساب الرقم الصحيح للنموذج الجديد
        const currentFormIndex = $('.distribution-item').length;
        console.log('Current forms count:', currentFormIndex);
        console.log('إضافة نموذج جديد برقم:', currentFormIndex);

        if (currentFormIndex < maxForms) {
            // إنشاء نموذج جديد دائماً
            createNewFormWithIndex(currentFormIndex);
        } else {
            alert('تم الوصول للحد الأقصى من عناصر التوزيع');
        }
    });

    // إنشاء نموذج جديد بفهرس محدد
    function createNewFormWithIndex(index) {
        console.log('إنشاء نموذج جديد برقم:', index);
        const newFormHtml = `
            <div class="distribution-item border p-3 mb-3" data-form-index="${index}">
                <input type="hidden" name="distribution_items-${index}-id" id="id_distribution_items-${index}-id">
                <input type="hidden" name="distribution_items-${index}-distribution" id="id_distribution_items-${index}-distribution">

                <div class="row">
                    <div class="col-md-3">
                        <div class="mb-3">
                            <label for="id_distribution_items-${index}-customer" class="form-label">العميل</label>
                            <div class="input-group">
                                <select name="distribution_items-${index}-customer" id="id_distribution_items-${index}-customer" class="form-select">
                                    <option value="">---------</option>
                                </select>
                                <button type="button" class="btn btn-success add-customer-btn" title="إضافة عميل جديد">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="mb-3">
                            <label for="id_distribution_items-${index}-driver" class="form-label">اسم السائق</label>
                            <input type="text" name="distribution_items-${index}-driver" id="id_distribution_items-${index}-driver" class="form-control">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="mb-3">
                            <label for="id_distribution_items-${index}-chicks_count" class="form-label">عدد الكتاكيت</label>
                            <input type="number" name="distribution_items-${index}-chicks_count" id="id_distribution_items-${index}-chicks_count" class="form-control" min="1">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="mb-3">
                            <label for="id_distribution_items-${index}-price_per_unit" class="form-label">السعر للوحدة</label>
                            <input type="number" name="distribution_items-${index}-price_per_unit" id="id_distribution_items-${index}-price_per_unit" class="form-control" step="0.01">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="mb-3">
                            <label for="id_distribution_items-${index}-paid_amount" class="form-label">المبلغ المدفوع</label>
                            <input type="number" name="distribution_items-${index}-paid_amount" id="id_distribution_items-${index}-paid_amount" class="form-control" step="0.01">
                        </div>
                    </div>
                    <div class="col-md-1 d-flex align-items-end">
                        <div class="mb-3">
                            <button type="button" class="btn btn-danger btn-sm remove-item" title="حذف هذا العنصر">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-12">
                        <div class="mb-3">
                            <label for="id_distribution_items-${index}-notes" class="form-label">ملاحظات</label>
                            <textarea name="distribution_items-${index}-notes" id="id_distribution_items-${index}-notes" class="form-control" rows="2"></textarea>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('#distribution-items').append(newFormHtml);

        // تحميل قائمة العملاء للنموذج الجديد
        loadCustomers(index);

        // تحديث العداد
        formCount = $('.distribution-item').length;
        updateFormCount();

        // تحديث الإحصائيات
        updateStatistics();

        console.log('تم إضافة نموذج جديد. العدد الحالي:', formCount);
    }

    // إنشاء نموذج جديد من الصفر (للتوافق مع الكود القديم)
    function createNewForm() {
        const currentFormIndex = $('.distribution-item').length;
        createNewFormWithIndex(currentFormIndex);
    }



    // تحميل قائمة العملاء
    function loadCustomers(formIndex) {
        const select = $(`#id_distribution_items-${formIndex}-customer`);
        select.empty();
        select.append('<option value="">---------</option>');

        // استخدام البيانات المحملة مسبقاً إذا كانت متاحة
        if (window.customersData && window.customersData.length > 0) {
            window.customersData.forEach(function(customer) {
                select.append(`<option value="${customer.id}">${customer.name}</option>`);
            });
            console.log(`تم تحميل ${window.customersData.length} عميل للنموذج ${formIndex} من البيانات المحملة مسبقاً`);
        } else {
            // محاولة تحميل البيانات من API كحل احتياطي
            $.ajax({
                url: '/hatchery/api/customers/',
                method: 'GET',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(data) {
                    select.empty();
                    select.append('<option value="">---------</option>');

                    data.forEach(function(customer) {
                        select.append(`<option value="${customer.id}">${customer.name}</option>`);
                    });
                    console.log(`تم تحميل ${data.length} عميل للنموذج ${formIndex} من API`);
                },
                error: function(xhr, status, error) {
                    console.log('خطأ في تحميل قائمة العملاء:', error);
                    select.append('<option value="">خطأ في تحميل العملاء</option>');
                }
            });
        }
    }

    // تحديث الإحصائيات
    function updateStatistics() {
        let totalDistributed = 0;
        $('.distribution-item input[name*="-chicks_count"]').each(function() {
            const value = parseInt($(this).val()) || 0;
            totalDistributed += value;
        });

        const totalAvailable = parseInt($('#total-available').text()) || 0;
        const totalRemaining = totalAvailable - totalDistributed;

        $('#total-distributed').text(totalDistributed);
        $('#total-remaining').text(totalRemaining);

        // تغيير لون المتبقي حسب الحالة
        const remainingSpan = $('#total-remaining');
        if (totalRemaining < 0) {
            remainingSpan.css('color', 'red').css('font-weight', 'bold');
        } else if (totalRemaining === 0) {
            remainingSpan.css('color', 'green').css('font-weight', 'bold');
        } else {
            remainingSpan.css('color', 'blue').css('font-weight', 'normal');
        }
    }

    // إضافة أحداث للنماذج
    function attachFormEvents(form) {
        // حساب الإجمالي عند تغيير الكمية أو السعر
        form.find('input[name*="-chicks_count"], input[name*="-price_per_unit"]').on('input', function() {
            const name = $(this).attr('name');
            const parts = name.split('-');
            const formPrefix = parts[0] + '-' + parts[1];
            const quantity = parseFloat($(`input[name="${formPrefix}-chicks_count"]`).val()) || 0;
            const price = parseFloat($(`input[name="${formPrefix}-price_per_unit"]`).val()) || 0;
            const total = quantity * price;

            // تحديث الإحصائيات
            updateStatistics();

            console.log(`الإجمالي للنموذج ${formPrefix}: ${total}`);
        });
    }

    // إضافة أحداث للنماذج الموجودة
    $('.distribution-item').each(function() {
        attachFormEvents($(this));
    });

    // تحديث الإحصائيات عند تحميل الصفحة
    updateStatistics();

    // إظهار قسم التوزيع عند تحميل الصفحة
    toggleDistributionSection();

    // إظهار/إخفاء قسم التوزيع حسب اختيار الدفعات
    function toggleDistributionSection() {
        // في صفحة التحديث، نظهر القسم دائماً
        if (window.location.pathname.includes('/update/')) {
            $('#distribution-section').show();
            return;
        }

        const checked = $('input[name="selected_hatchings"]:checked').length;
        console.log('Selected hatchings:', checked);
        if (checked > 0) {
            $('#distribution-section').show();
        } else {
            $('#distribution-section').hide();
            // مسح عناصر التوزيع
            $('#distribution-items').empty();
            $('#id_distribution_items-TOTAL_FORMS').val('0');
            formCount = 0;
        }
    }

    // تحديد/إلغاء تحديد جميع الدفعات
    $('#select-all-batches').change(function() {
        $('input[name="selected_hatchings"]').prop('checked', this.checked);
        toggleDistributionSection();
    });

    // تحديث حالة "تحديد الكل" عند تغيير أي دفعة
    $('input[name="selected_hatchings"]').change(function() {
        const total = $('input[name="selected_hatchings"]').length;
        const checked = $('input[name="selected_hatchings"]:checked').length;
        $('#select-all-batches').prop('checked', total === checked);
        toggleDistributionSection();
    });

    // التحقق الأولي
    toggleDistributionSection();

    // مراقبة إرسال النموذج
    $('#merged-distribution-form').on('submit', function(e) {
        console.log('تم إرسال النموذج');

        // في صفحة التحديث، لا نحتاج للتحقق من اختيار الدفعات
        if (!window.location.pathname.includes('/update/')) {
            // التحقق من اختيار دفعات (فقط في صفحة الإنشاء)
            const selectedBatches = $('input[name="selected_hatchings"]:checked').length;
            if (selectedBatches === 0) {
                e.preventDefault();
                alert('يرجى اختيار دفعة واحدة على الأقل للدمج');
                return false;
            }
        }

        // طباعة بيانات النموذج للتشخيص
        const formData = new FormData(this);
        console.log('بيانات النموذج:');
        let distributionItemsCount = 0;
        for (const pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
            if (pair[0].startsWith('distribution_items-') && !pair[0].includes('FORMS')) {
                distributionItemsCount++;
            }
        }
        console.log('عدد حقول عناصر التوزيع:', distributionItemsCount);

        return true; // السماح بإرسال النموذج
    });

    // حذف عنصر توزيع
    $(document).on('click', '.remove-item', function(e) {
        e.preventDefault();
        $(this).closest('.distribution-item').remove();

        // إعادة ترقيم النماذج
        renumberForms();
    });

    // إعادة ترقيم النماذج بعد الحذف
    function renumberForms() {
        $('.distribution-item').each(function(index) {
            const form = $(this);

            // تحديث جميع الحقول في النموذج
            form.find('input, select, textarea').each(function() {
                const name = $(this).attr('name');
                const id = $(this).attr('id');

                if (name && name.includes('distribution_items-')) {
                    const newName = name.replace(/distribution_items-\d+/, 'distribution_items-' + index);
                    $(this).attr('name', newName);
                }

                if (id && id.includes('distribution_items-')) {
                    const newId = id.replace(/distribution_items-\d+/, 'distribution_items-' + index);
                    $(this).attr('id', newId);
                }
            });

            // تحديث labels
            form.find('label').each(function() {
                const forAttr = $(this).attr('for');
                if (forAttr && forAttr.includes('distribution_items-')) {
                    const newFor = forAttr.replace(/distribution_items-\d+/, 'distribution_items-' + index);
                    $(this).attr('for', newFor);
                }
            });

            // تحديث data attribute
            form.attr('data-form-index', index);
        });

        // تحديث عداد النماذج
        formCount = $('.distribution-item').length;
        updateFormCount();

        // تحديث الإحصائيات
        updateStatistics();
    }

    // إضافة عميل جديد
    $(document).on('click', '.add-customer-btn', function(e) {
        e.preventDefault();
        openCustomerPopup(this);
    });

    // فتح نافذة منبثقة لإضافة عميل جديد
    function openCustomerPopup(button) {
        const customerSelect = $(button).closest('.input-group').find('select');
        const popupWindow = window.open('/hatchery/customers/create/?is_popup=true', 'newCustomer', 'width=600,height=700');

        // استقبال رسالة من النافذة المنبثقة
        const messageHandler = function(event) {
            if (event.data && event.data.type === 'new_customer') {
                const customer = event.data.customer;

                // إضافة العميل الجديد إلى جميع قوائم العملاء
                $('select[id$="-customer"]').each(function() {
                    const option = $('<option></option>').attr('value', customer.id).text(customer.name);
                    $(this).append(option);

                    // تحديد العميل الجديد في القائمة التي تم النقر عليها
                    if (this === customerSelect[0]) {
                        $(this).val(customer.id);
                    }
                });

                // إضافة العميل إلى البيانات المحملة مسبقاً
                if (window.customersData) {
                    window.customersData.push({
                        id: customer.id,
                        name: customer.name
                    });
                }

                // إزالة مستمع الأحداث
                window.removeEventListener('message', messageHandler);

                console.log('تم إضافة عميل جديد:', customer.name);
            }
        };

        window.addEventListener('message', messageHandler);
    }
});
