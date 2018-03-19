%define major 2
%define privmaj 0
%define api 1.0
%define libname %mklibname %{name} %{major}
%define libpriv %mklibname colordprivate %{major}
%define libhug %mklibname colorhug %{major}
%define girname %mklibname %{name}-gir %{api}
%define girhug %mklibname colorhug-gir %{api}
%define devname %mklibname %{name} -d

# Building the extra print profiles requires colprof, +4Gb of RAM and
# quite a lot of time. Don't enable this for test builds.
%bcond_without print_profiles

# SANE is pretty insane when it comes to handling devices, and we get AVCs
# popping up all over the place.
%bcond_without sane
%bcond_with docs

Summary:	Color daemon
Name:		colord
Version:	1.4.1
Release:	1
License:	GPLv2+ and LGPLv2+
Group:		System/X11
Url:		http://www.freedesktop.org/software/colord/
Source0:	http://www.freedesktop.org/software/colord/releases/%{name}-%{version}.tar.xz

BuildRequires:	docbook-utils
BuildRequires:	gettext
BuildRequires:	gtk-doc
BuildRequires:	intltool
BuildRequires:	vala-tools
%if %{with sane}
BuildRequires:	sane-devel
%endif
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(bash-completion)
BuildRequires:	pkgconfig(gobject-introspection-1.0)
BuildRequires:	pkgconfig(gudev-1.0)
BuildRequires:	pkgconfig(gusb)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(polkit-gobject-1)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	pkgconfig(libudev)
BuildRequires:	meson
%if %{with print_profiles}
BuildRequires:	hargyllcms
%endif
Requires(pre,postun):	rpm-helper
Requires:	shared-color-profiles

# obsolete separate profiles package
Obsoletes:	shared-color-profiles <= 0.1.6-10
Provides:	shared-color-profiles = %{EVRD}
# obsolete separate profiles package
Obsoletes:	shared-color-profiles-extra <= 0.1.6-10
Provides:	shared-color-profiles-extra = %{EVRD}

%description
colord is a low level system activated daemon that maps color devices
to color profiles in the system context.

%package -n %{libname}
Summary:	Library package for %{name}
Group:		System/Libraries

%description -n %{libname}
Main library for %{name}.

%package -n %{libpriv}
Summary:	Library package for %{name}
Group:		System/Libraries

%description -n %{libpriv}
Main library for %{name}.

%package -n %{libhug}
Summary:	Library package for %{name}
Group:		System/Libraries

%description -n %{libhug}
Main library for %{name}.

%package -n %{girname}
Summary:	GObject Introspection interface description for %{name}
Group:		System/Libraries

%description -n %{girname}
GObject Introspection interface description for %{name}.

%package -n %{girhug}
Summary:	GObject Introspection interface description for ColorHug
Group:		System/Libraries

%description -n %{girhug}
GObject Introspection interface description for ColorHug

%package -n %{devname}
Summary:	Development package for %{name}
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libpriv} = %{version}-%{release}
Requires:	%{libhug} = %{version}-%{release}
Requires:	%{girname} = %{version}-%{release}
Requires:	%{girhug} = %{version}-%{release}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Files for development with %{name}.

%prep
%setup -q

%build
export CFLAGS='-fPIC %optflags'
export LDFLAGS='-pie -Wl,-z,now -Wl,-z,relro'
%ifnarch %arm
# Set ~2 GiB limit so that colprof is forced to work in chunks when
# generating the print profile rather than trying to allocate a 3.1 GiB
# chunk of RAM to put the entire B-to-A tables in.
ulimit -Sv 2000000
%endif

# (tpg) ugly workaround !
# we have polkit 0.113 patched with few cherry-picks form upstream
# so it is safe to call that 0.113 a 0.114 here
sed -i -e "s/polkit.version().version_compare('>= 0.114')/polkit.version().version_compare('>= 0.114')/" meson.build

%meson \
    -Dwith-daemon-user="colord" \
%if %{with docs}
    -Denable-docs=false \
%endif
%if %{with print_profiles}
    -Denable-print-profiles=true \
%endif
%if %{with sane}
    -Denable-sane=true \
%endif
    -Denable-vala=true

%meson_build

%install
%meson_install

# databases
touch %{buildroot}%{_localstatedir}/lib/colord/mapping.db
touch %{buildroot}%{_localstatedir}/lib/colord/storage.db

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-colord.preset << EOF
enable colord.service
EOF

%find_lang %{name}

%pre
%_pre_useradd colord /var/lib/colord /sbin/nologin
%_pre_groupadd colord colord

%postun
%_postun_userdel colord
%_postun_groupdel colord

%files -f %{name}.lang
%doc AUTHORS NEWS
%{_datadir}/bash-completion/completions/colormgr
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.ColorManager.conf
/lib/udev/rules.d/*.rules
%{_bindir}/*
%{_libexecdir}/colord
%if %{with sane}
%{_libexecdir}/colord-sane
%endif
%{_libexecdir}/colord-session
%{_libdir}/colord-plugins/*.so
%{_libdir}/colord-sensors/*.so
%dir %{_datadir}/color/icc/colord
%{_datadir}/color/icc/colord/*.ic?
%{_datadir}/colord/icons/*.svg
%{_datadir}/colord/ti1/*.ti1
%{_datadir}/colord/illuminant
%{_datadir}/colord/cmf
%{_datadir}/colord/ref
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorHelper.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager*.xml
%{_datadir}/dbus-1/services/org.freedesktop.ColorHelper.service
%{_datadir}/dbus-1/system-services/org.freedesktop.ColorManager.service
%{_datadir}/glib-2.0/schemas/org.freedesktop.ColorHelper.gschema.xml
%{_datadir}/polkit-1/actions/org.freedesktop.color.policy
%{_mandir}/man1/*.1.*
%attr(755,colord,colord) %dir %{_localstatedir}/lib/colord
%attr(755,colord,colord) %dir %{_localstatedir}/lib/colord/icc
%ghost %{_localstatedir}/lib/colord/*.db
%{_presetdir}/86-colord.preset
%{_systemunitdir}/*.service
%{_userunitdir}/*.service
%{_tmpfilesdir}/*.conf

%files -n %{libname}
%{_libdir}/libcolord.so.%{major}*

%files -n %{libpriv}
%{_libdir}/libcolordprivate.so.%{major}*

%files -n %{libhug}
%{_libdir}/libcolorhug.so.%{major}*

%files -n %{girname}
%{_libdir}/girepository-1.0/Colord-%{api}.typelib

%files -n %{girhug}
%{_libdir}/girepository-1.0/ColorHug-%{api}.typelib

%files -n %{devname}
%{_includedir}/colord-1
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%{_datadir}/gir-1.0/*.gir
%{_datadir}/vala/vapi/*.vapi
