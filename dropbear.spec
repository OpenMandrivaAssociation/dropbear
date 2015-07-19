# (tmb) temp linking fix
%define _disable_ld_as_needed 1
%define _disable_ld_no_undefined 1
%define year 2014

%bcond_without	uclibc

Name:		dropbear
Version:	2015.67
Release:	2
Summary:	SSH2 server and client

Group:		Networking/Remote access
License:	MIT
URL:		http://matt.ucc.asn.au/dropbear/dropbear.html
Source0:	http://matt.ucc.asn.au/dropbear/releases/%{name}-%{version}.tar.bz2
Source1:	dropbear.service
Source2:	dropbear-keygen.service
Patch0:		dropbear-2014.63-whole-program.patch

BuildRequires:	zlib-devel >= 1.2.7-5
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-16
%endif
BuildRequires:	pam-devel
Requires(post):	rpm-helper >= 0.24.8-1
Requires(preun):rpm-helper >= 0.24.8-1

Requires:	initscripts
Requires(post):	chkconfig >= 0.9, initscripts

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
%apply_patches

# convert CHANGES to UTF-8
iconv -f iso-8859-1 -t utf-8 -o CHANGES{.utf8,}
mv CHANGES{.utf8,}

%build
mkdir -p glibc
pushd glibc
CONFIGURE_TOP=.. \
%configure	--enable-pam
%make -k || make
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
		--disable-pam \
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
cp %{name}.8 glibc/
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
install -d %{buildroot}%{_mandir}/man1
install -m 0644 dbclient.1 %{buildroot}%{_mandir}/man1/dbclient.1
install -d %{buildroot}%{_mandir}/man8
install -m 0644 dropbearkey.1 %{buildroot}%{_mandir}/man1/dropbearkey.1

chmod a+r CHANGES INSTALL LICENSE MULTI README SMALL TODO

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%files
%doc CHANGES INSTALL LICENSE MULTI README SMALL TODO
%dir %{_sysconfdir}/dropbear
%{_unitdir}/dropbear*
%{_bindir}/dropbearkey
%{_bindir}/dropbearconvert
%{_bindir}/dbclient
%{_sbindir}/dropbear
%{_mandir}/man1/dbclient.1*
%{_mandir}/man1/dropbearkey.1*
%{_mandir}/man8/dropbear.8*

%if %{with uclibc}
%files -n uclibc-dropbear
%{uclibc_root}%{_bindir}/dropbearmulti
%{uclibc_root}%{_bindir}/scp
%{uclibc_root}%{_bindir}/ssh
%{uclibc_root}%{_sbindir}/dropbear
%endif
