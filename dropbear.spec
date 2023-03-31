# (tmb) temp linking fix
%define _disable_ld_as_needed 1
%define _disable_ld_no_undefined 1

Name:		dropbear
Version:	2022.83
Release:	2
Summary:	SSH2 server and client

Group:		Networking/Remote access
License:	MIT
URL:		http://matt.ucc.asn.au/dropbear/dropbear.html
Source0:	http://matt.ucc.asn.au/dropbear/releases/%{name}-%{version}.tar.bz2
Source1:	dropbear.service
Source2:	dropbear-keygen.service
BuildRequires:	zlib-devel >= 1.2.7-5
BuildRequires:	pam-devel

%description
Dropbear is a relatively small SSH 2 server and client.  Dropbear
is particularly useful for "embedded"-type Linux (or other Unix)
systems, such as wireless routers.

%prep
%autosetup -p1

%build
CPPFLAGS='-DSFTPSERVER_PATH=\"%{_libdir}/ssh/sftp-server\"' %configure --enable-pam

%make_build -k || make


%install
%make_install

install -d %{buildroot}%{_sysconfdir}/dropbear
install -d %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/dropbear.service
install -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/dropbear-keygen.service
install -d %{buildroot}%{_mandir}/man1
install -m 0644 dbclient.1 %{buildroot}%{_mandir}/man1/dbclient.1
install -d %{buildroot}%{_mandir}/man8
install -m 0644 dropbearkey.1 %{buildroot}%{_mandir}/man1/dropbearkey.1

chmod a+r CHANGES INSTALL LICENSE MULTI README SMALL

install -d %{buildroot}%{_sysconfdir}/sysconfig
cat > %{buildroot}%{_sysconfdir}/sysconfig/dropbear << EOF
OPTIONS=""
EOF

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-dropbear.preset << EOF
enable dropbear.service
EOF

%files
%doc CHANGES INSTALL LICENSE MULTI README SMALL
%dir %{_sysconfdir}/dropbear
%config(noreplace) %{_sysconfdir}/sysconfig/dropbear
%{_presetdir}/86-dropbear.preset
%{_unitdir}/dropbear*
%{_bindir}/dropbearkey
%{_bindir}/dropbearconvert
%{_bindir}/dbclient
%{_sbindir}/dropbear
%{_mandir}/man1/dbclient.1*
%{_mandir}/man1/dropbearkey.1*
%{_mandir}/man1/dropbearconvert.1*
%{_mandir}/man8/dropbear.8*
