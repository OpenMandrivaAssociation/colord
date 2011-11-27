%define major 1
%define gir_major 1.0
%define libname %mklibname %{name} %{major}
%define girname %mklibname %{name}-gir %{gir_major}
%define develname %mklibname %{name} -d

Summary:	Color daemon
Name:		colord
Version:	0.1.15
Release:	1
License:	GPLv2+ and LGPLv2+
Group:		System/X11
URL:		http://www.freedesktop.org/software/colord/
Source0:	http://www.freedesktop.org/software/colord/releases/%{name}-%{version}.tar.xz
BuildRequires:	docbook-utils
BuildRequires:	gettext
BuildRequires:	intltool
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gobject-introspection-1.0)
BuildRequires:	pkgconfig(gudev-1.0)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(polkit-gobject-1)
BuildRequires:	pkgconfig(sqlite)
BuildRequires:	sane-devel
BuildRequires:	vala-tools

Requires:	shared-color-profiles

%description
colord is a low level system activated daemon that maps color devices
to color profiles in the system context.

%package -n %{libname}
Summary:	Library package for %{name}
Group:		System/Libraries

%description -n %{libname}
Main library for %{name}.

%package -n %{girname}
Summary:	GObject Introspection interface description for %{name}
Group:		System/Libraries
Requires:	%{libname} = %{version}-%{release}

%description -n %{girname}
GObject Introspection interface description for %{name}.

%package -n %{develname}
Summary:	Development package for %{name}
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
Files for development with %{name}.

%prep
%setup -q

%build
%configure \
	--disable-static \
   	--disable-rpath \
   	--disable-examples \
   	--disable-dependency-tracking

%make

%install
%makeinstall_std

# Remove static libs and libtool archives.
find %{buildroot} -name '*.la' -exec rm -f {} ';'

# databases
touch %{buildroot}%{_localstatedir}/lib/colord/mapping.db
touch %{buildroot}%{_localstatedir}/lib/colord/storage.db

%find_lang %{name}

%files -f %{name}.lang
%doc README AUTHORS NEWS
%config %{_sysconfdir}/colord.conf
%dir %{_localstatedir}/lib/colord
%dir %{_datadir}/color/icc/colord
/lib/udev/rules.d/*.rules
%{_bindir}/*
%{_libdir}/colord
%{_libdir}/colord-sensors
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.ColorManager.conf
%{_datadir}/dbus-1/interfaces/org.freedesktop.ColorManager*.xml
%{_datadir}/polkit-1/actions/org.freedesktop.color.policy
%{_datadir}/dbus-1/system-services/org.freedesktop.ColorManager.service
%{_datadir}/man/man1/*.1.*
%{_datadir}/color/icc/colord/*.ic?
%ghost %{_localstatedir}/lib/colord/*.db

%files -n %{libname}
%{_libdir}/libcolord.so.%{major}*

%files -n %{girname}
%{_libdir}/girepository-1.0/Colord-%{gir_major}.typelib

%files -n %{develname}
%{_includedir}/colord-1
%{_libdir}/libcolord.so
%{_libdir}/pkgconfig/colord.pc
%{_datadir}/gir-1.0/*.gir
%{_datadir}/vala/vapi/*.vapi

