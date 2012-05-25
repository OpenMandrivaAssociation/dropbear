# (tmb) temp linking fix
%define _disable_ld_as_needed 1
%define _disable_ld_no_undefined 1
%define year 2012

Name:		dropbear
Version:	2012.55
Release:	4
Summary:	SSH2 server and client

Group:		Networking/Remote access
License:	MIT
URL:		http://matt.ucc.asn.au/dropbear/dropbear.html
Source0:	http://matt.ucc.asn.au/dropbear/releases/%{name}-%{version}.tar.bz2
Source1:	dropbear.service
Source2:	dropbear-keygen.service
Source3:	dropbear.init

BuildRequires:	zlib-devel
# (cg) I tried enabling pam but it seems somewhat broken and doesn't
# register with systemd-logind for now. Should be fixed.
# https://bugzilla.redhat.com/show_bug.cgi?id=770251
#BuildRequires:	libpam-devel
%if 0
Requires(post):	rpm-helper >= 0.24.8-1
Requires(preun):rpm-helper >= 0.24.8-1

Requires:	initscripts
Requires(post):	chkconfig >= 0.9, initscripts
%endif

%description
Dropbear is a relatively small SSH 2 server and client.  Dropbear
is particularly useful for "embedded"-type Linux (or other Unix)
systems, such as wireless routers.

%prep
%setup -q

# convert CHANGES to UTF-8
iconv -f iso-8859-1 -t utf-8 -o CHANGES{.utf8,}
mv CHANGES{.utf8,}

%build
%configure
# --enable-pam
%make

%install
%makeinstall_std
install -d %{buildroot}%{_sysconfdir}/dropbear
install -d %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/dropbear.service
install -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/dropbear-keygen.service
install -d %{buildroot}%{_initrddir}
install -m 0755 %{SOURCE3} %{buildroot}%{_initrddir}/dropbear
install -d %{buildroot}%{_mandir}/man1
install -m 0644 dbclient.1 %{buildroot}%{_mandir}/man1/dbclient.1
install -d %{buildroot}%{_mandir}/man8
install -m 0644 dropbear.8 %{buildroot}%{_mandir}/man8/dropbear.8
install -m 0644 dropbearkey.8 %{buildroot}%{_mandir}/man8/dropbearkey.8

chmod a+r CHANGES INSTALL LICENSE MULTI README SMALL TODO

# we leave it disabled for now..
%if 0
%post
%_post_service %{name}

%preun
%_preun_service %{name}
%endif

%files
%doc CHANGES INSTALL LICENSE MULTI README SMALL TODO
%dir %{_sysconfdir}/dropbear
%{_unitdir}/dropbear*
%{_initrddir}/dropbear
%{_bindir}/dropbearkey
%{_bindir}/dropbearconvert
%{_bindir}/dbclient
%{_sbindir}/dropbear
%{_mandir}/man1/dbclient.1*
%{_mandir}/man8/dropbear.8*
%{_mandir}/man8/dropbearkey.8*
