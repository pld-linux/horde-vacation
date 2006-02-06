%define		_hordeapp	vacation
%define		_rel	0.2
#
%include	/usr/lib/rpm/macros.php
Summary:	vacation - vacation manager module for Horde
Summary(pl):	vacation - modu³ zarz±dzania wakacjami dla Horde
Name:		horde-%{_hordeapp}
Version:	2.2.2
Release:	%{?_rc:0.%{_rc}.}%{?_snap:0.%(echo %{_snap} | tr -d -).}%{_rel}
License:	ASL
Group:		Applications/WWW
#Source0:	ftp://ftp.horde.org/pub/snaps/%{_snap}/%{_hordeapp}-HEAD-%{_snap}.tar.gz
Source0:	ftp://ftp.horde.org/pub/vacation/%{_hordeapp}-%{version}.tar.gz
# Source0-md5:	1345ff8e30a98de7085f01f0abde3007
Source1:	%{name}.conf
URL:		http://www.horde.org/vacation/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.226
BuildRequires:	tar >= 1:1.15.1
Requires:	apache >= 1.3.33-2
Requires:	apache(mod_access)
Requires:	horde >= 3.0
Requires:	php-xml >= 4.1.0
Requires:	vacation
Requires:	webapps
Requires:	webserver = apache
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# horde accesses it directly in help->about
%define		_noautocompressdoc  CREDITS
%define		_noautoreq	'pear(Horde.*)'

%define		hordedir	/usr/share/horde
%define		_appdir		%{hordedir}/%{_hordeapp}
%define		_webapps	/etc/webapps
%define		_webapp		horde-%{_hordeapp}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
Vacation is a Horde module for managing user e-mail "vacation notices"
or "auto-responders." It works via a local vacation program which must
be installed and functioning on the server. It supports vacation
programs using the .forward-style forwarding mechanism supported by
several popular mailers, as well as qmail and SQL based
implementations. While it has been released and is in production use
at many sites, it is also under heavy development in an effort to
expand and improve the module.

%description -l pl
Vacation to modu³ Horde do zarz±dzania pocztowymi "powiadomieniami o
wakacjach" czy te¿ "autoresponderami" u¿ytkowników. Dzia³a poprzez
lokalny program vacation, który musi byæ zainstalowany i dzia³aj±cy na
serwerze. Obs³uguje programy vacation u¿ywaj±ce mechanizmu
przekazywania typu .forward obs³ugiwanego przez kilka popularnych
programów pocztowych, a tak¿e implementacje oparte na qmailu i SQL-u.
Choæ modu³ zosta³ wydany i jest u¿ywany produkcyjnie na wielu
serwerach, jest nadal intensywnie rozwijany w celu rozszerzenia i
ulepszenia modu³u.

%prep
%setup -q -c -T -n %{?_snap:%{_hordeapp}-%{_snap}}%{!?_snap:%{_hordeapp}-%{version}%{?_rc:-%{_rc}}}
tar zxf %{SOURCE0} --strip-components=1

rm -f scripts/.htaccess
# considered harmful (horde/docs/SECURITY)
rm -f test.php

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir} \
	$RPM_BUILD_ROOT%{_appdir}/{docs,graphics,lib,locale,scripts,templates}

cp -pR	*.php			$RPM_BUILD_ROOT%{_appdir}
for i in config/*.dist; do
	cp -p $i $RPM_BUILD_ROOT%{_sysconfdir}/$(basename $i .dist)
done
echo '<?php ?>' > $RPM_BUILD_ROOT%{_sysconfdir}/conf.php
touch	$RPM_BUILD_ROOT%{_sysconfdir}/conf.php.bak

cp -pR	graphics/*		$RPM_BUILD_ROOT%{_appdir}/graphics
cp -pR	lib/*			$RPM_BUILD_ROOT%{_appdir}/lib
cp -pR	locale/*		$RPM_BUILD_ROOT%{_appdir}/locale
cp -pR	templates/*		$RPM_BUILD_ROOT%{_appdir}/templates

ln -s %{_sysconfdir} $RPM_BUILD_ROOT%{_appdir}/config
ln -s %{_docdir}/%{name}-%{version}/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs

install %{SOURCE1} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/conf.php.bak
fi

%triggerin -- apache1
%webapp_register apache %{_webapp}

%triggerun -- apache1
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- horde-%{_hordeapp} < 2.2.2-0.2, %{_hordeapp}
for i in conf.php longIntro.txt mime_drivers.php prefs.php sourceroots.php; do
	if [ -f /etc/horde.org/%{_hordeapp}/$i.rpmsave ]; then
		mv -f %{_sysconfdir}/$i{,.rpmnew}
		mv -f /etc/horde.org/%{_hordeapp}/$i.rpmsave %{_sysconfdir}/$i
	fi
done

if [ -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave ]; then
	mv -f %{_sysconfdir}/apache.conf{,.rpmnew}
	mv -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	cp -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave %{_sysconfdir}/apache.conf
	cp -f /etc/horde.org/apache-%{_hordeapp}.conf.rpmsave %{_sysconfdir}/httpd.conf
fi

if [ -L /etc/apache/conf.d/99_horde-%{_hordeapp}.conf ]; then
	/usr/sbin/webapp register apache %{_webapp}
	rm -f /etc/apache/conf.d/99_horde-%{_hordeapp}.conf
	%service -q apache reload
fi
if [ -L /etc/httpd/httpd.conf/99_horde-%{_hordeapp}.conf ]; then
	/usr/sbin/webapp register httpd %{_webapp}
	rm -f /etc/httpd/httpd.conf/99_horde-%{_hordeapp}.conf
	%service -q httpd reload
fi

%files
%defattr(644,root,root,755)
%doc README docs/* scripts
%attr(750,root,http) %dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/httpd.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/conf.php.bak

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/graphics
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
