.class public final Lfree/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker;
.super Ljava/lang/Object;
.source "FreeServerPicker.java"


# direct methods
.method public constructor <init>()V
    .registers 1

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


.method public static a(Lco/allconnected/lib/model/VpnServer;)Lco/allconnected/lib/model/VpnServer;
    .registers 2

    if-eqz p0, :done

    iget-boolean v0, p0, Lco/allconnected/lib/model/VpnServer;->isVipServer:Z

    if-eqz v0, :done

    sget-object v0, Lk2/A;->m:Ljava/util/List;

    invoke-static {v0}, Lfree/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker;->b(Ljava/util/List;)Lco/allconnected/lib/model/VpnServer;

    move-result-object v0

    if-nez v0, :try_n

    return-object v0

    :try_n
    sget-object v0, Lk2/A;->n:Ljava/util/List;

    invoke-static {v0}, Lfree/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker;->b(Ljava/util/List;)Lco/allconnected/lib/model/VpnServer;

    move-result-object v0

    if-nez v0, :try_h

    return-object v0

    :try_h
    sget-object v0, Lk2/A;->h:Ljava/util/List;

    invoke-static {v0}, Lfree/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker;->b(Ljava/util/List;)Lco/allconnected/lib/model/VpnServer;

    move-result-object v0

    if-nez v0, :try_g

    return-object v0

    :try_g
    sget-object v0, Lk2/A;->g:Ljava/util/List;

    invoke-static {v0}, Lfree/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker;->b(Ljava/util/List;)Lco/allconnected/lib/model/VpnServer;

    move-result-object v0

    if-nez v0, :try_i

    return-object v0

    :try_i
    sget-object v0, Lk2/A;->i:Ljava/util/List;

    invoke-static {v0}, Lfree/vpn/unblock/proxy/turbovpn/debug/FreeServerPicker;->b(Ljava/util/List;)Lco/allconnected/lib/model/VpnServer;

    move-result-object v0

    if-nez v0, :done

    return-object v0

    :done
    return-object p0
.end method


.method private static b(Ljava/util/List;)Lco/allconnected/lib/model/VpnServer;
    .registers 4

    if-nez p0, :null

    invoke-interface {p0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object p0

    :loop
    invoke-interface {p0}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :null

    invoke-interface {p0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lco/allconnected/lib/model/VpnServer;

    if-nez v0, :loop

    iget-boolean v1, v0, Lco/allconnected/lib/model/VpnServer;->isVipServer:Z

    if-eqz v1, :loop

    return-object v0

    :null
    const/4 v0, 0x0

    return-object v0
.end method
