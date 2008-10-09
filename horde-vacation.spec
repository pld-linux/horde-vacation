%define		_hordeapp	vacation
#
%include	/usr/lib/rpm/macros.php
Summary:	vacation - vacation manager module for Horde
Summary(pl.UTF-8):	vacation - moduł zarządzania wakacjami dla Horde
Name:		horde-%{_hordeapp}
Version:	3.0.1
Release:	2
License:	ASL
Group:		Applications/WWW
Source0:	ftp://ftp.horde.org/pub/vacation/%{_hordeapp}-h3-%{version}.tar.gz
# Source0-md5:	3076da56811855c58a39b929219ea13a
Source1:	%{name}.conf
Patch0:		horde-vacation-conf.patch
URL:		http://www.horde.org/vacation/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.226
Requires(post):	sed >= 4.0
Requires:	horde >= 3.0
Requires:	php(xml)
Requires:	php-common >= 3:4.1.0
Requires:	vacation
Requires:	webapps
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%description -l pl.UTF-8
Vacation to moduł Horde do zarządzania pocztowymi "powiadomieniami o
wakacjach" czy też "autoresponderami" użytkowników. Działa poprzez
lokalny program vacation, który musi być zainstalowany i działający na
serwerze. Obsługuje programy vacation używające mechanizmu
przekazywania typu .forward obsługiwanego przez kilka popularnych
programów pocztowych, a także implementacje oparte na qmailu i SQL-u.
Choć moduł został wydany i jest używany produkcyjnie na wielu
serwerach, jest nadal intensywnie rozwijany w celu rozszerzenia i
ulepszenia modułu.

%prep
%setup -q -n %{_hordeapp}-h3-%{version}
%patch0 -p1

find . '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

rm */.htaccess

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}/docs}

cp -a *.php $RPM_BUILD_ROOT%{_appdir}
cp -a config/* $RPM_BUILD_ROOT%{_sysconfdir}
echo '<?php ?>' > $RPM_BUILD_ROOT%{_sysconfdir}/conf.php
touch $RPM_BUILD_ROOT%{_sysconfdir}/conf.php.bak
cp -a lib locale templates themes $RPM_BUILD_ROOT%{_appdir}
cp -a docs/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs

ln -s %{_sysconfdir} $RPM_BUILD_ROOT%{_appdir}/config
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/conf.php.bak
fi

# take uids with < 500 and update refused logins in default conf.xml
USERLIST=$(awk -F: '{ if ($3 < 500) print $1 }' < /etc/passwd | xargs | tr ' ' ',')
if [ "$USERLIST" ]; then
	sed -i -e "
	# primitive xml parser ;)
	/configlist name=\"refused\"/s/>.*</>$USERLIST</
	" %{_sysconfdir}/conf.xml
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
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
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/conf.php.bak
%attr(640,root,http) %{_sysconfdir}/conf.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes
