%define rname           TuxGuitar
%define section         free
%define gcj_support     1
%define javac_target    1.5

Name:           tuxguitar
Version:        1.0
Release:        %mkrel 0.0.5
Epoch:          0
Summary:        Multitrack guitar tablature editor and player
License:        LGPL
Group:          Sound
URL:            http://www.tuxguitar.com.ar/
Source0:        http://download.sourceforge.net/sourceforge/tuxguitar/tuxguitar-src-%{version}.tar.gz
Source1:        %{name}-script
Source2:        %{name}.desktop
Source3:        %{name}-build.properties
Requires:       aoss
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
Requires:       eclipse-swt
Requires:       java
Requires:       jpackage-utils
Requires:       itext
BuildRequires:  alsa-lib-devel
BuildRequires:  ant
BuildRequires:  desktop-file-utils
# FIXME: (walluck): This doesn't seem to produce the correct output
%if 0
BuildRequires:  docbook-to-man
%endif
BuildRequires:  eclipse-swt
BuildRequires:  fluidsynth-devel
BuildRequires:  java-rpmbuild
BuildRequires:  itext
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildRequires:  java-devel
BuildArch:      noarch
%endif
Provides:       %{rname} = %{epoch}:%{version}-%{release}
Provides:       %{name}-alsa = %{epoch}:%{version}-%{release}
Obsoletes:      %{name}-alsa < %{epoch}:%{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

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
%setup -q -n %{name}-src-%{version}
# All of this is to fix the JNI location
%{__cp} -a %{SOURCE3} TuxGuitar/build.properties
%{__perl} -pi -e 's|^lib.swt.jni=.*|lib.swt.jni=%{_libdir}/eclipse|' TuxGuitar/build.properties
%{__perl} -pi -e 's|-Dbuild\.jni\.library\.dir=.*|-Dbuild.jni.library.dir=%{_libdir}/eclipse|' Makefile
%{__perl} -pi -e 's|/usr/lib/jni|%{_libdir}/eclipse|' TuxGuitar/xml/build-mac.xml TuxGuitar/xml/build-linux.xml TuxGuitar/xml/build-ubuntu.xml

%build
export CLASSPATH=
export OPT_JAR_LIST=:
%{__make} \
  JNI_OS=linux \
  JAVA_HOME=%{java_home} \
  JAVA_VERS=%{javac_target} \
  ITEXT_JAR=$(build-classpath itext) \
  SWT_JAR=$(build-classpath swt) \

for pkg in TuxGuitar TuxGuitar-CoreAudio TuxGuitar-alsa TuxGuitar-ascii TuxGuitar-ftp TuxGuitar-compat TuxGuitar-converter TuxGuitar-fluidsynth TuxGuitar-gtp TuxGuitar-jsa TuxGuitar-lilypond TuxGuitar-midi TuxGuitar-musicxml TuxGuitar-oss TuxGuitar-pdf TuxGuitar-ptb TuxGuitar-tef TuxGuitar-tray TuxGuitar-winmm; do
    if [ ! -d ${pkg}/src ]; then
        echo "Skipping ${pkg}"
        continue
    fi

    %{__mkdir_p} api/${pkg}

    pushd ${pkg}/src
        %{javadoc} -quiet -d ../../api/${pkg} `find . -type f -name "*.java"` || echo "Building javadocs for ${pkg} failed"
    popd
done

%if 0
pushd misc
%{__rm} tuxguitar.1
%{_bindir}/docbook-to-man tuxguitar.sgml > tuxguitar.1
popd
%endif

%install
%{__rm} -rf %{buildroot}

export DESTDIR=%{buildroot}

%{__make} \
PREFIX=${DESTDIR}%{_prefix} \
INSTALL_BIN_DIR=${DESTDIR}%{_bindir} \
INSTALL_LIB_DIR=${DESTDIR}%{_libdir} \
INSTALL_DOC_DIR=${DESTDIR}%{_docdir}/%{name} \
INSTALL_SHARE_DIR=${DESTDIR}%{_datadir}/%{name} \
INSTALL_JAR_DIR=${DESTDIR}%{_javadir} \
install install-linux

%{__mkdir_p} %{buildroot}%{_javadir}
%{__mv} %{buildroot}%{_javadir}/tuxguitar.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)

(cd %{buildroot}%{_datadir}/%{name} && %{__ln_s} %{buildroot}%{_javadir}/%{name}.jar tuxguitar.jar)

%{__mkdir_p} %{buildroot}%{_datadir}/tuxguitar/plugins
for plugin in `find . -type f -name 'tuxguitar-*.jar'`; do
    %{__cp} -a ${plugin} %{buildroot}%{_datadir}/tuxguitar/plugins
done

%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__perl} -pe \
  's|/usr/lib|%{_libdir}|g ;
   s|/usr/share/tuxguitar|%{_datadir}/%{name}|g' \
  %{SOURCE1} > %{buildroot}%{_bindir}/%{name}
%{__chmod} 755 %{buildroot}%{_bindir}/%{name}

%{__mkdir_p} %{buildroot}%{_datadir}/pixmaps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/16x16/apps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/32x32/apps
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
%{__install} -p -m 0644 TuxGuitar/share/skins/ersplus/icon-32x32.png %{buildroot}%{_datadir}/pixmaps/%{name}.png
%{__install} -p -m 0644 TuxGuitar/share/skins/ersplus/icon-16x16.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{__install} -p -m 0644 TuxGuitar/share/skins/ersplus/icon-32x32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{__install} -p -m 0644 TuxGuitar/share/skins/ersplus/icon-64x64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{name}.png

%{__mkdir_p} %{buildroot}%{_datadir}/applications
%{_bindir}/desktop-file-install --vendor ""                     \
        --dir ${RPM_BUILD_ROOT}%{_datadir}/applications         \
        %{SOURCE2}

%{__mkdir_p} %{buildroot}%{_datadir}/application-registry
%{__install} -p -m 0644 misc/tuxguitar.xml %{buildroot}%{_datadir}/application-registry/%{name}.applications

%{__mkdir_p} %{buildroot}%{_mandir}/man1
%{__cp} -a misc/tuxguitar.1 %{buildroot}%{_mandir}/man1/%{name}.1

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

%post
%if %{gcj_support}
%{update_gcjdb}
%endif
%if %mdkversion < 200900
%{update_desktop_database}
%{update_mime_database}
%update_icon_cache hicolor
%endif

%postun
%if %{gcj_support}
%{clean_gcjdb}
%endif
%if %mdkversion < 200900
%{clean_desktop_database}
%{clean_mime_database}
%clean_icon_cache hicolor
%endif

%files
%defattr(0644,root,root,0755)
%doc AUTHORS ChangeLog COPYING LICENSE README
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
%{_libdir}/*.so
%{_mandir}/man1/%{name}.1*

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}
