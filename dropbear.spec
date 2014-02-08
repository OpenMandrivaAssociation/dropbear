# (tmb) temp linking fix
%define _disable_ld_as_needed 1
%define _disable_ld_no_undefined 1
%define year 2013

%bcond_without	uclibc

Name:		dropbear
Version:	2013.58
Release:	2
Summary:	SSH2 server and client

Group:		Networking/Remote access
License:	MIT
URL:		http://matt.ucc.asn.au/dropbear/dropbear.html
Source0:	http://matt.ucc.asn.au/dropbear/releases/%{name}-%{version}.tar.bz2
Source1:	dropbear.service
Source2:	dropbear-keygen.service
Source3:	dropbear.init
# hackish, I hate automake..
Patch0:		dropbear-2012.55-whole-program.patch

BuildRequires:	zlib-devel >= 1.2.7-5
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-16
%endif
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

%package -n	uclibc-dropbear
Summary:	Minimalistic uClibc linked build of dropbear

%description -n	uclibc-dropbear
Dropbear is a relatively small SSH 2 server and client.  Dropbear
is particularly useful for "embedded"-type Linux (or other Unix)
systems, such as wireless routers.
This package contains an extremely small and minimalistic build.


%prep
%setup -q
%patch0 -p1 -b .whole_program~

# convert CHANGES to UTF-8
iconv -f iso-8859-1 -t utf-8 -o CHANGES{.utf8,}
mv CHANGES{.utf8,}

%build
mkdir -p glibc
pushd glibc
CONFIGURE_TOP=.. \
%configure
# --enable-pam
%make
popd

%if %{with uclibc}
# too much trouble doing build out of source dir, automake blows..
#mkdir -p uclibc
#pushd uclibc
CONFIGURE_TOP=. \
COLLECT_CC=uclibc-gcc \
CFLAGS="%{uclibc_cflags} -flto -ffunction-sections -fdata-sections -fwhole-program" \
LDFLAGS="-Wl,--gc-sections %{ldflags} -Wl,-O2 -flto -Wl,--no-warn-common"
%uclibc_configure \
		--disable-lastlog \
		--disable-utmp \
		--disable-utmpx \
		--disable-wtmp \
		--disable-wtmpx \
		--disable-loginfunc \
		--disable-pututline \
		--disable-pututxline \
		--enable-zlib \
		--disable-shadow
%make MULTI=1 WHOLE_PROGRAM=1 dropbearmulti STATIC=0 PROGRAMS="dropbear dbclient scp"
#popd
%endif

%install
%makeinstall_std -C glibc
%if %{with uclibc}
install -m755 dropbearmulti -D %{buildroot}%{uclibc_root}%{_bindir}/dropbearmulti
ln %{buildroot}%{uclibc_root}%{_bindir}/dropbearmulti %{buildroot}%{uclibc_root}%{_bindir}/scp
ln %{buildroot}%{uclibc_root}%{_bindir}/dropbearmulti %{buildroot}%{uclibc_root}%{_bindir}/ssh
mkdir -p %{buildroot}%{uclibc_root}%{_sbindir}
ln %{buildroot}%{uclibc_root}%{_bindir}/dropbearmulti %{buildroot}%{uclibc_root}%{_sbindir}/dropbear
%endif

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

%if %{with uclibc}
%files -n uclibc-dropbear
%{uclibc_root}%{_bindir}/dropbearmulti
%{uclibc_root}%{_bindir}/scp
%{uclibc_root}%{_bindir}/ssh
%{uclibc_root}%{_sbindir}/dropbear
%endif

%changelog
* Sun Oct 28 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 2012.55-8
+ Revision: 820210
- use %%uclibc_configure macro
- create links for dropbear, ssh & scp from multibinary
- link uClibc build dynamically
- reenable zlib for uClibc build
- build with scp support in uclibc multibinary
- make a static binary the proper way...
- disable zlib & shadow for uClibc build
- make a super small build using -fwhole-program & uClibc (P0)

* Fri May 25 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 2012.55-4
+ Revision: 800525
- imported from mageia, needed by drakx-installer-rescue..
- imported package dropbear

* Sat Apr 28 2012 tmb <tmb> 2012.55-3.mga2
+ Revision: 233679
- Require rpm-helper >= 0.24.8-1 for systemd support
- rebuild for versioned rpm-helper requires

* Sun Apr 22 2012 colin <colin> 2012.55-1.mga2
+ Revision: 232534
- New version: 2012.55 (CVE-2012-0920)
- Add systemd support (PAM registration is broken)
- Adapt spec to Mageia

* Mon Apr 25 2011 stormi <stormi> 0.53.1-2.mga1
+ Revision: 90810
- fix RPM group

* Mon Apr 25 2011 tmb <tmb> 0.53.1-1.mga1
+ Revision: 90190
- imported package dropbear

* Sun Apr 24 2011 Thomas Backlund <tmb@mageia.org> 0.53.1-1.mga1
- update to 0.53.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.52-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Apr 19 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 0.52-1
- New version 0.5.2

