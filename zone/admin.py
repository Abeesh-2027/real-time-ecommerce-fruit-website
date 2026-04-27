from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Fruit, Order, OrderItem


# ---------------- FRUIT ADMIN ----------------
@admin.register(Fruit)
class FruitAdmin(admin.ModelAdmin):
    list_display    = ('name', 'price', 'preview_image', 'is_active', 'created_at')
    list_filter     = ('is_active',)
    search_fields   = ('name',)
    list_editable   = ('price', 'is_active')
    ordering        = ('name',)
    readonly_fields = ('created_at', 'preview_image')

    fieldsets = (
        ('Product Info', {'fields': ('name', 'price', 'is_active')}),
        ('Image', {
            'fields': ('image', 'image_file', 'preview_image'),
            'description': 'Upload an image OR enter a static filename.'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:6px;" />',
                obj.image.url
            )
        if obj.image_file:
            return format_html(
                '<span style="color:#aaa;font-size:12px;">Static: {}</span>',
                obj.image_file
            )
        return '—'
    preview_image.short_description = 'Preview'


# ---------------- ORDER ITEM INLINE ----------------
class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ('name', 'price', 'quantity', 'line_total', 'image_url')
    fields          = ('name', 'price', 'quantity', 'line_total', 'image_url')
    can_delete      = False

    def has_add_permission(self, request, obj=None):
        return False


# ---------------- ORDER ADMIN ----------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'customer_name', 'customer_phone',
        'total_display', 'payment_method',
        'status',           # ✅ FIX: added this
        'status_badge',
        'created_at'
    )

    list_filter   = ('status', 'payment_method', 'created_at')
    search_fields = ('order_id', 'customer_name', 'customer_email', 'customer_phone')
    ordering      = ('-created_at',)

    list_editable = ('status',)   # ✅ now valid

    date_hierarchy = 'created_at'
    inlines        = [OrderItemInline]

    readonly_fields = (
        'order_id', 'customer_name', 'customer_phone', 'customer_email',
        'delivery_address', 'delivery_notes',
        'subtotal', 'delivery_charge', 'total',
        'payment_method', 'razorpay_payment_id',
        'created_at', 'updated_at',
    )

    fieldsets = (
        ('Order Info', {
            'fields': ('order_id', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'customer_email',
                       'delivery_address', 'delivery_notes')
        }),
        ('Payment', {
            'fields': ('payment_method', 'razorpay_payment_id')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_charge', 'total')
        }),
    )

    def total_display(self, obj):
        return format_html(
            '<strong style="color:#2FAE2E;">₹{}</strong>',
            obj.total
        )
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'

    def status_badge(self, obj):
        colours = {
            'confirmed': ('#e8f5e9', '#2e7d32'),
            'delivered': ('#e3f2fd', '#1565c0'),
            'cancelled': ('#fce4ec', '#c62828'),
            'pending':   ('#fff8e1', '#f57f17'),
        }
        bg, fg = colours.get(obj.status, ('#f5f5f5', '#555'))
        return format_html(
            '<span style="background:{};color:{};padding:4px 12px;'
            'border-radius:20px;font-size:12px;font-weight:700;">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        extra_context = extra_context or {}

        extra_context['summary'] = {
            'total_orders':  qs.count(),
            'total_revenue': qs.filter(status__in=['confirmed', 'delivered'])
                               .aggregate(rev=Sum('total'))['rev'] or 0,
            'confirmed':     qs.filter(status='confirmed').count(),
            'delivered':     qs.filter(status='delivered').count(),
            'cancelled':     qs.filter(status='cancelled').count(),
        }

        return super().changelist_view(request, extra_context=extra_context)


# ---------------- ORDER ITEM ADMIN ----------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display    = ('order', 'name', 'price', 'quantity', 'line_total')
    search_fields   = ('name', 'order__order_id')
    list_filter     = ('order__status',)
    ordering        = ('-order__created_at',)
    readonly_fields = ('order', 'name', 'price', 'quantity', 'image_url', 'line_total')

    def has_add_permission(self, request):
        return False


# ---------------- ADMIN UI ----------------
admin.site.site_header  = '🍎 Fruitzone Admin'
admin.site.site_title   = 'Fruitzone'
admin.site.index_title  = 'Fruitzone Dashboard'