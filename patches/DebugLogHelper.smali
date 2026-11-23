.class public final Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;
.super Ljava/lang/Object;
.source "DebugLogHelper.java"

# interfaces
.implements Landroid/view/View$OnClickListener;
.implements Ljava/lang/Runnable;


# static fields
.field private static f:Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;


# instance fields
.field private a:Landroid/app/Activity;

.field private b:Landroid/widget/TextView;

.field private c:Landroid/widget/ScrollView;

.field private d:Landroid/os/Handler;

.field private e:Landroid/widget/PopupWindow;

.field private g:Z


.method public constructor <init>(Landroid/app/Activity;)V
    .registers 2

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    return-void
.end method


.method public static a(Landroid/app/Activity;)V
    .registers 4

    sget-object v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->f:Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;

    if-eqz v0, :create

    iget-object v1, v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    if-eq v1, p0, :create

    iget-object v1, v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->e:Landroid/widget/PopupWindow;

    if-eqz v1, :create

    invoke-virtual {v1}, Landroid/widget/PopupWindow;->isShowing()Z

    move-result v1

    if-eqz v1, :create

    return-void

    :create
    if-eqz v0, :new

    iget-object v1, v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->e:Landroid/widget/PopupWindow;

    if-eqz v1, :new

    invoke-virtual {v1}, Landroid/widget/PopupWindow;->dismiss()V

    :new
    new-instance v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;

    invoke-direct {v0, p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;-><init>(Landroid/app/Activity;)V

    sput-object v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->f:Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;

    invoke-direct {v0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b()V

    return-void
.end method


.method private b()V
    .registers 16

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    new-instance v1, Landroid/widget/LinearLayout;

    invoke-direct {v1, v0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->setOrientation(I)V

    const v2, 0xff101010

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    new-instance v2, Landroid/widget/TextView;

    invoke-direct {v2, v0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v3, "TURBO VPN LOG   \u2022   TAP HERE TO COPY"

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/4 v3, -0x1

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextColor(I)V

    const/high16 v3, 0x41700000

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextSize(F)V

    sget-object v3, Landroid/graphics/Typeface;->DEFAULT_BOLD:Landroid/graphics/Typeface;

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V

    const v3, 0xffd50000

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setBackgroundColor(I)V

    const/16 v3, 0x10

    invoke-virtual {v2, v3, v3, v3, v3}, Landroid/widget/TextView;->setPadding(IIII)V

    invoke-virtual {v2, p0}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    new-instance v3, Landroid/widget/ScrollView;

    invoke-direct {v3, v0}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    new-instance v4, Landroid/widget/TextView;

    invoke-direct {v4, v0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v5, "Reading logcat..."

    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/4 v5, -0x1

    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setTextColor(I)V

    const/high16 v5, 0x41200000

    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setTextSize(F)V

    sget-object v5, Landroid/graphics/Typeface;->MONOSPACE:Landroid/graphics/Typeface;

    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V

    const v5, 0xff000000

    invoke-virtual {v4, v5}, Landroid/widget/TextView;->setBackgroundColor(I)V

    const/16 v5, 0x8

    invoke-virtual {v4, v5, v5, v5, v5}, Landroid/widget/TextView;->setPadding(IIII)V

    invoke-virtual {v4, p0}, Landroid/widget/TextView;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    invoke-virtual {v3, v4}, Landroid/widget/ScrollView;->addView(Landroid/view/View;)V

    new-instance v5, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v6, -0x1

    const/4 v7, 0x0

    invoke-direct {v5, v6, v7}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    const/high16 v6, 0x3f800000

    iput v6, v5, Landroid/widget/LinearLayout$LayoutParams;->weight:F

    invoke-virtual {v1, v3, v5}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    iput-object v4, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    iput-object v3, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->c:Landroid/widget/ScrollView;

    invoke-virtual {v0}, Landroid/app/Activity;->getResources()Landroid/content/res/Resources;

    move-result-object v5

    invoke-virtual {v5}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v5

    iget v5, v5, Landroid/util/DisplayMetrics;->heightPixels:I

    const/16 v6, 0x1e

    mul-int/2addr v5, v6

    const/16 v6, 0x64

    div-int/2addr v5, v6

    new-instance v6, Landroid/widget/PopupWindow;

    const/4 v7, -0x1

    const/4 v8, 0x0

    invoke-direct {v6, v1, v7, v5, v8}, Landroid/widget/PopupWindow;-><init>(Landroid/view/View;IIZ)V

    invoke-virtual {v6, v8}, Landroid/widget/PopupWindow;->setFocusable(Z)V

    const/4 v9, 0x1

    invoke-virtual {v6, v9}, Landroid/widget/PopupWindow;->setTouchable(Z)V

    invoke-virtual {v6, v8}, Landroid/widget/PopupWindow;->setOutsideTouchable(Z)V

    new-instance v9, Landroid/graphics/drawable/ColorDrawable;

    const v10, 0xff101010

    invoke-direct {v9, v10}, Landroid/graphics/drawable/ColorDrawable;-><init>(I)V

    invoke-virtual {v6, v9}, Landroid/widget/PopupWindow;->setBackgroundDrawable(Landroid/graphics/drawable/Drawable;)V

    const/high16 v9, 0x41c00000

    invoke-virtual {v6, v9}, Landroid/widget/PopupWindow;->setElevation(F)V

    iput-object v6, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->e:Landroid/widget/PopupWindow;

    invoke-virtual {v0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v5

    invoke-virtual {v5}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v5

    invoke-virtual {v5, p0}, Landroid/view/View;->post(Ljava/lang/Runnable;)Z

    return-void
.end method


.method private c()V
    .registers 5

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    if-nez v0, :done

    invoke-virtual {v0}, Landroid/widget/TextView;->getText()Ljava/lang/CharSequence;

    move-result-object v0

    invoke-interface {v0}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;

    move-result-object v0

    iget-object v1, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    const-string v2, "clipboard"

    invoke-virtual {v1, v2}, Landroid/app/Activity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Landroid/content/ClipboardManager;

    const-string v2, "Turbo VPN log"

    invoke-static {v2, v0}, Landroid/content/ClipData;->newPlainText(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Landroid/content/ClipData;

    move-result-object v2

    invoke-virtual {v1, v2}, Landroid/content/ClipboardManager;->setPrimaryClip(Landroid/content/ClipData;)V

    iget-object v1, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    const-string v2, "LOG COPIED - paste it in the chat"

    const/4 v3, 0x1

    invoke-static {v1, v2, v3}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v1

    invoke-virtual {v1}, Landroid/widget/Toast;->show()V

    :done
    return-void
.end method


# virtual methods
.method public b(Ljava/lang/String;)V
    .registers 4

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    if-nez v0, :done

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->c:Landroid/widget/ScrollView;

    if-nez v0, :scroll

    const/16 v1, 0x82

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->fullScroll(I)Z

    :scroll
    iget-boolean v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->g:Z

    if-eqz v0, :done

    invoke-direct {p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->c()V

    const/4 v0, 0x1

    iput-boolean v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->g:Z

    :done
    return-void
.end method

.method public onClick(Landroid/view/View;)V
    .registers 2

    invoke-direct {p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->c()V

    return-void
.end method

.method public run()V
    .registers 6

    sget-object v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->f:Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;

    if-eq v0, p0, :done

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    invoke-virtual {v0}, Landroid/app/Activity;->isFinishing()Z

    move-result v1

    if-eqz v1, :done

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->e:Landroid/widget/PopupWindow;

    if-eqz v0, :refresh

    invoke-virtual {v0}, Landroid/widget/PopupWindow;->isShowing()Z

    move-result v1

    if-eqz v1, :refresh

    iget-object v1, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    invoke-virtual {v1}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v1

    invoke-virtual {v1}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v1

    if-eqz v1, :refresh

    const/16 v2, 0x30

    const/4 v3, 0x0

    :try_start_show
    invoke-virtual {v0, v1, v2, v3, v3}, Landroid/widget/PopupWindow;->showAtLocation(Landroid/view/View;III)V
    :try_end_show
    goto :refresh

    :catch_show
    move-exception v1

    :refresh
    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    if-nez v0, :done

    new-instance v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogTask;

    invoke-direct {v0, p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogTask;-><init>(Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;)V

    const/4 v1, 0x0

    new-array v1, v1, [Ljava/lang/Object;

    invoke-virtual {v0, v1}, Landroid/os/AsyncTask;->execute([Ljava/lang/Object;)Landroid/os/AsyncTask;

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->d:Landroid/os/Handler;

    if-nez v0, :have_handler

    new-instance v0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    iput-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->d:Landroid/os/Handler;

    :have_handler
    const-wide/16 v1, 0x5dc

    invoke-virtual {v0, p0, v1, v2}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    :done
    return-void

    .catch Landroid/view/WindowManager$BadTokenException; {:try_start_show .. :try_end_show} :catch_show
    .catch Ljava/lang/RuntimeException; {:try_start_show .. :try_end_show} :catch_show
.end method
