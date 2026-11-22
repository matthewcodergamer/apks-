.class public final Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;
.super Ljava/lang/Object;
.source "DebugLogHelper.java"

# interfaces
.implements Landroid/view/View$OnClickListener;
.implements Landroid/view/View$OnLongClickListener;
.implements Ljava/lang/Runnable;


# instance fields
.field private a:Landroid/app/Activity;

.field private b:Landroid/widget/TextView;

.field private c:Landroid/widget/ScrollView;

.field private d:Landroid/os/Handler;


# direct methods
.method public constructor <init>(Landroid/app/Activity;)V
    .registers 2

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    return-void
.end method

.method public static a(Landroid/app/Activity;)V
    .registers 8

    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const-string v1, "turbo_debug_log"

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewWithTag(Ljava/lang/Object;)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :done

    new-instance v0, Landroid/widget/Button;

    invoke-direct {v0, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    const-string v1, "LOG"

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    const-string v1, "turbo_debug_log"

    invoke-virtual {v0, v1}, Landroid/view/View;->setTag(Ljava/lang/Object;)V

    const/4 v1, -0x1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTextColor(I)V

    const v1, 0xcc000000

    invoke-virtual {v0, v1}, Landroid/view/View;->setBackgroundColor(I)V

    const/16 v1, 0x10

    invoke-virtual {v0, v1, v1, v1, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    new-instance v2, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;

    invoke-direct {v2, p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;-><init>(Landroid/app/Activity;)V

    invoke-virtual {v0, v2}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    invoke-virtual {v0, v2}, Landroid/view/View;->setOnLongClickListener(Landroid/view/View$OnLongClickListener;)V

    const v1, 0x1020002

    invoke-virtual {p0, v1}, Landroid/app/Activity;->findViewById(I)Landroid/view/View;

    move-result-object v1

    if-eqz v1, :done

    check-cast v1, Landroid/view/ViewGroup;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v3, -0x2

    invoke-direct {v2, v3, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    const/16 v3, 0x30

    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->gravity:I

    const/16 v3, 0x10

    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->leftMargin:I

    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->topMargin:I

    invoke-virtual {v1, v0, v2}, Landroid/view/ViewGroup;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

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

    if-nez v0, :done

    const/16 v1, 0x82

    invoke-virtual {v0, v1}, Landroid/widget/ScrollView;->fullScroll(I)Z

    :done
    return-void
.end method

.method public onClick(Landroid/view/View;)V
    .registers 10

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    invoke-virtual {v0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const-string v1, "turbo_debug_overlay"

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewWithTag(Ljava/lang/Object;)Landroid/view/View;

    move-result-object v0

    if-eqz v0, :show

    invoke-virtual {v0}, Landroid/view/View;->getParent()Landroid/view/ViewParent;

    move-result-object v1

    if-eqz v1, :clear

    check-cast v1, Landroid/view/ViewGroup;

    invoke-virtual {v1, v0}, Landroid/view/ViewGroup;->removeView(Landroid/view/View;)V

    :clear
    const/4 v0, 0x0

    iput-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    iput-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->c:Landroid/widget/ScrollView;

    return-void

    :show
    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->a:Landroid/app/Activity;

    new-instance v1, Landroid/widget/ScrollView;

    invoke-direct {v1, v0}, Landroid/widget/ScrollView;-><init>(Landroid/content/Context;)V

    const-string v2, "turbo_debug_overlay"

    invoke-virtual {v1, v2}, Landroid/view/View;->setTag(Ljava/lang/Object;)V

    new-instance v2, Landroid/widget/TextView;

    invoke-direct {v2, v0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v3, "Loading log..."

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/4 v3, -0x1

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextColor(I)V

    const/high16 v3, 0x41100000

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTextSize(F)V

    sget-object v3, Landroid/graphics/Typeface;->MONOSPACE:Landroid/graphics/Typeface;

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V

    const v3, 0xdd101010

    invoke-virtual {v2, v3}, Landroid/view/View;->setBackgroundColor(I)V

    const/16 v3, 0x8

    invoke-virtual {v2, v3, v3, v3, v3}, Landroid/widget/TextView;->setPadding(IIII)V

    const/16 v3, 0x14

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setMaxLines(I)V

    invoke-virtual {v1, v2}, Landroid/widget/ScrollView;->addView(Landroid/view/View;)V

    iput-object v2, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    iput-object v1, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->c:Landroid/widget/ScrollView;

    const v3, 0x1020002

    invoke-virtual {v0, v3}, Landroid/app/Activity;->findViewById(I)Landroid/view/View;

    move-result-object v3

    if-eqz v3, :schedule

    check-cast v3, Landroid/view/ViewGroup;

    new-instance v4, Landroid/widget/FrameLayout$LayoutParams;

    const/4 v5, -0x1

    const/4 v6, -0x2

    invoke-direct {v4, v5, v6}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    const/16 v5, 0x50

    iput v5, v4, Landroid/widget/FrameLayout$LayoutParams;->gravity:I

    invoke-virtual {v3, v1, v4}, Landroid/view/ViewGroup;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    :schedule
    iget-object v3, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->d:Landroid/os/Handler;

    if-nez v3, :have_handler

    new-instance v3, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v4

    invoke-direct {v3, v4}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    iput-object v3, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->d:Landroid/os/Handler;

    :have_handler
    invoke-virtual {v3, p0}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    return-void
.end method

.method public onLongClick(Landroid/view/View;)Z
    .registers 6

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    if-nez v0, :false

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

    const-string v2, "Log copied"

    const/4 v3, 0x0

    invoke-static {v1, v2, v3}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v1

    invoke-virtual {v1}, Landroid/widget/Toast;->show()V

    const/4 v0, 0x1

    return v0

    :false
    const/4 v0, 0x0

    return v0
.end method

.method public run()V
    .registers 5

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->b:Landroid/widget/TextView;

    if-nez v0, :done

    new-instance v0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogTask;

    invoke-direct {v0, p0}, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogTask;-><init>(Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;)V

    const/4 v1, 0x0

    new-array v1, v1, [Ljava/lang/Object;

    invoke-virtual {v0, v1}, Landroid/os/AsyncTask;->execute([Ljava/lang/Object;)Landroid/os/AsyncTask;

    iget-object v0, p0, Lfree/vpn/unblock/proxy/turbovpn/debug/DebugLogHelper;->d:Landroid/os/Handler;

    if-eqz v0, :done

    const-wide/16 v1, 0x5dc

    invoke-virtual {v0, p0, v1, v2}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    :done
    return-void
.end method
