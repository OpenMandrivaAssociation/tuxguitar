%define rname           TuxGuitar
%define section         free
%define gcj_support     1

Name:           tuxguitar
Version:        0.9.1
Release:        %mkrel 9
Epoch:          0
Summary:        Multitrack guitar tablature editor and player
License:        LGPL
Group:          Development/Java
URL:            http://www.herac.com.ar/tuxguitar.html
Source0:        http://download.sourceforge.net/sourceforge/tuxguitar/TuxGuitar-%{version}-src.tar.gz
Source1:        %{name}-script
Source2:        %{name}.desktop
Source3:        %{name}.applications
Requires:       aoss
Requires:       java
Requires:       jpackage-utils >= 0:1.6
Requires:       itext
Requires:       libswt3-gtk2 = 1:3.3.0
BuildRequires:  ant
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  itext
BuildRequires:  libswt3-gtk2
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildRequires:  java-devel
BuildArch:      noarch
%endif
BuildRequires:  java-devel-icedtea
Provides:       %{rname} = %{epoch}:%{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:  desktop-file-utils
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description
TuxGuitar is a multitrack guitar tablature editor and player written
in Java-SWT.

With TuxGuitar, you will be able to compose music using the
following features:

    * Tablature editor
    * Multitrack display
    * Autoscroll while playing
    * Note duration management
    * Various effects (bend, slide, vibrato, hammer-on/pull-off)
    * Support for triplets (5,6,7,9,10,11,12)
    * Repeat open and close
    * Time signature management
    * Tempo management
    * Imports and exports gp3 and gp4 files

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{rname}-%{version}-src
%{__perl} -pi -e 's|<javac|<javac nowarn="true"|g' build.xml
%{__perl} -pi -e 's|<attribute name="Class-Path".*||g' build.xml

%build
export CLASSPATH=
export OPT_JAR_LIST=:
export JAVA_HOME=%{_jvmdir}/java-icedtea
ant \
  -Dbuild.manifest.classpath= \
  -Dlib.swt.jni=%{_libdir} \
  -Dlib.swt.jar=$(build-classpath swt-gtk-3.3) \
  -Dlib.itext.jar=$(build-classpath itext)

%{__mkdir_p} api
pushd src
%{javadoc} -d ../api `find . -type f -name "*.java"`
popd

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_javadir}
%{__cp} -a TuxGuitar.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)

%{__mkdir_p} %{buildroot}%{_bindir}
%{__perl} -pe \
  's|/usr/lib|%{_libdir}|g ;
   s|/usr/share/tuxguitar|%{_datadir}/%{name}|g' \
  %{SOURCE1} > %{buildroot}%{_bindir}/%{name}
%{__chmod} 755 %{buildroot}%{_bindir}/%{name}

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}
(cd share && %{__cp} -a files lang %{buildroot}%{_datadir}/%{name})

%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%{__mkdir_p} %{buildroot}%{_datadir}/pixmaps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/16x16/apps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/32x32/apps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
%{__install} -m 644 share/files/icon-32x32.png %{buildroot}%{_datadir}/pixmaps/%{name}.png
%{__install} -m 644 share/files/icon-16x16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{__install} -m 644 share/files/icon-32x32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{__install} -m 644 share/files/icon-64x64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{name}.png

%{__mkdir_p} %{buildroot}%{_datadir}/applications
%{_bindir}/desktop-file-install --vendor mandriva               \
        --dir ${RPM_BUILD_ROOT}%{_datadir}/applications         \
        --remove-category Application                           \
        --add-category X-MandrivaLinux-Multimedia-Sound         \
        %{SOURCE2}

%{__mkdir_p} %{buildroot}%{_datadir}/application-registry
%{__install} -m 644 %{SOURCE3} %{buildroot}%{_datadir}/application-registry

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

%post
%if %{gcj_support}
%{update_gcjdb}
%endif
%{update_desktop_database}
%{update_mime_database}
%update_icon_cache hicolor

%postun
%if %{gcj_support}
%{clean_gcjdb}
%endif
%{clean_desktop_database}
%{clean_mime_database}
%clean_icon_cache hicolor

%post javadoc
%{__rm} -f %{_javadocdir}/%{name}
%{__ln_s} %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ $1 -eq 0 ]; then
  %{__rm} -f %{_javadocdir}/%{name}
fi

%files
%defattr(0644,root,root,0755)
%doc doc/*
%attr(0755,root,root) %{_bindir}/%{name}
%{_javadir}/*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*.jar.*
%endif
%{_datadir}/%{name}
%{_datadir}/applications/*
%{_datadir}/application-registry/*
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{name}.png

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%ghost %doc %{_javadocdir}/%{name}
