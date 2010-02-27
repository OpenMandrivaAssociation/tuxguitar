%define rname           TuxGuitar
%define gcj_support     1

# For a hack to fix internal help browser to work.
# (Set correct path to MOZILLA_FIVE_HOME on runtime).
%define	mozappdir	%(rpm -q --queryformat='%%{name}-%%{version}' xulrunner)

Name:           tuxguitar
Version:        1.2
Release:        %mkrel 2
Summary:        Multitrack guitar tablature editor and player
License:        LGPLv2+
Group:          Sound
URL:            http://www.tuxguitar.com.ar/
Source0:	http://downloads.sourceforge.net/%{name}/%{name}-src-%{version}.tar.gz
# Use Fedora specific build script from upstream svn.
# http://tuxguitar.svn.sourceforge.net/viewvc/tuxguitar/trunk/TuxGuitar/xml/build-fedora.xml
Source1:	%{name}-build-fedora.xml
# From upstream trunk, to disable certain plugins by default
# http://tuxguitar.svn.sourceforge.net/viewvc/tuxguitar/trunk/TuxGuitar/src/org/herac/tuxguitar/gui/system/plugins/TGPluginProperties.java?r1=99&r2=770
Patch0:		%{name}-plugin-properties.patch

BuildRequires:	alsa-lib-devel
BuildRequires:	ant
BuildRequires:	ant-contrib
BuildRequires:	ant-nodeps
BuildRequires:	itext
BuildRequires:	desktop-file-utils
BuildRequires:	fluidsynth-devel
BuildRequires:	jackit-devel
BuildRequires:	java-devel-openjdk
BuildRequires:	java-rpmbuild
BuildRequires:	jpackage-utils
BuildRequires:	eclipse-swt

%if %{gcj_support}
BuildRequires:	java-gcj-compat-devel
Requires(post):	java-gcj-compat
Requires(postun):	java-gcj-compat
%else
BuildArch:	noarch
%endif

Requires:       eclipse-swt
Requires:       java >= 1.6
Requires:	jpackage-utils
Requires:       itext

Provides:       %{rname} = %{version}-%{release}
Provides:       %{name}-alsa = %{version}-%{release}
Obsoletes:      %{name}-alsa < %{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
TuxGuitar is a multitrack guitar tablature editor and player written
in Java-SWT.

With TuxGuitar, you will be able to compose music using the
following features:

    * Tablature editor
    * Score Viewer
    * Multitrack display
    * Autoscroll while playing
    * Note duration management
    * Various effects (bend, slide, vibrato, hammer-on/pull-off)
    * Support for triplets (5,6,7,9,10,11,12)
    * Repeat open and close
    * Time signature management
    * Tempo management
    * Imports and exports gp3, gp4 and gp5 files

%prep
%setup -q -n %{name}-src-%{version}
%patch0 -p1

cp %{SOURCE1} TuxGuitar/xml/build-fedora.xml

# Set debug="true" on javac part of the build scripts.
for file in $(find . -name build.xml); do
   sed -i 's|debug="false"|debug="true"|' $file
done

# Bump Java requires to 1.5
for file in $(find . -name build.properties); do
   sed -i 's|1.4|1.5|g' $file
done

# Use a hack to set correct path to MOZILLA_FIVE_HOME on runtime.
# Fixes internal help browser not working.
sed -i 's,firefox,%{mozappdir},' TuxGuitar/xml/build-fedora.xml

%build
# Plugins to build:
PLUGINS="alsa ascii browser-ftp community compat converter fluidsynth gervill\
         gtp jack jsa lilypond midi musicxml oss pdf ptb tef tray"

# JNI's to build
JNIS="alsa fluidsynth jack oss"

LIBSUFFIX=$(echo %{_lib}|sed 's|lib||')

# to pass to ant:
ANT_FLAGS=" \
   -Dpath.tuxguitar=$PWD/TuxGuitar/%{name}.jar \
   -Dpath.itext=%{_javadir}/itext.jar \
   -Dpath.swt=%{_libdir}/eclipse/swt.jar \
   -Dlib.swt.jar=%{_libdir}/eclipse/swt.jar \
   -Ddist.lib.path=%{_libdir}/%{name}/ \
   -Ddist.file=xml/build-fedora.xml \
   -Ddist.jar.path=%{_datadir}/%{name}/ \
   -Ddist.share.path=%{_datadir}/%{name}/ \
   -Dos.lib.suffix=$LIBSUFFIX \
   -Dos.data.dir=%{_datadir}/ \
   -Ddist.default.style=Lavender \
   -Ddist.default.song=%{_datadir}/%{name}/%{name}.tg"

# build jars
%{ant} -f TuxGuitar/build.xml -v -d $ANT_FLAGS all
for jarname in $PLUGINS; do
   %{ant} -f TuxGuitar-$jarname/build.xml -v -d $ANT_FLAGS \
      -Dbuild.jar=../TuxGuitar/share/plugins/tuxguitar-$jarname.jar all
done

# build jnis
for jni in $JNIS; do
   %{make} -C TuxGuitar-$jni/jni CFLAGS="%{optflags} \
              -I%{_jvmdir}/java-openjdk/include \
              -I%{_jvmdir}/java-openjdk/include/linux \
              -fPIC"
done

%install
rm -rf %{buildroot}

# to pass to ant:
ANT_FLAGS=" \
   -Dpath.tuxguitar=$PWD/TuxGuitar/%{name}.jar \
   -Ddist.file=xml/build-fedora.xml \
   -Dos.bin.dir=%{_bindir} \
   -Ddist.jar.path=%{_datadir}/%{name}/ \
   -Ddist.share.path=%{_datadir}/%{name}/ \
   -Dos.lib.suffix=$LIBSUFFIX \
   -Dos.data.dir=%{_datadir}/ \
   -Ddist.default.style=Lavender \
   -Ddist.doc.path=%{_docdir}/%{name}-%{version}/ \
   -Ddist.default.song=%{_datadir}/%{name}/%{name}.tg \
   -Ddist.dst.path=%{buildroot}"

%{ant} -f TuxGuitar/build.xml -v -d $ANT_FLAGS install

# install jnis we built
mkdir -p %{buildroot}%{_libdir}/%{name}
cp -a TuxGuitar-*/jni/*.so %{buildroot}%{_libdir}/%{name}/

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root,-)
%{_docdir}/%{name}-%{version}
%{_libdir}/%{name}
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/icons/hicolor/*/mimetypes/*.png
%{_datadir}/mime/packages/%{name}.xml

%if %{gcj_support}
%{_libdir}/gcj/%{name}
%endif
