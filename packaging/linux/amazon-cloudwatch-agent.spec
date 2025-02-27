Summary:    Amazon CloudWatch Agent
Name:       amazon-cloudwatch-agent
Version:    %{AGENT_VERSION}
Release:    1
License:    MIT License. Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
Group:      Applications/CloudWatch-Agent

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot-%(%{__id_u} -n)
Source:     amazon-cloudwatch-agent.tar.gz

%define _enable_debug_packages 0
%define debug_package %{nil}

%prep
%setup -c %{name}-%{version}

%description
This package provides daemon of Amazon CloudWatch Agent

%install

rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
cp -r %{_topdir}/BUILD/%{name}-%{version}/*  $RPM_BUILD_ROOT/

############################# create the symbolic links
# bin
mkdir -p ${RPM_BUILD_ROOT}/usr/bin
ln -f -s /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl ${RPM_BUILD_ROOT}/usr/bin/amazon-cloudwatch-agent-ctl
# etc
mkdir -p ${RPM_BUILD_ROOT}/etc/amazon
ln -f -s /opt/aws/amazon-cloudwatch-agent/etc ${RPM_BUILD_ROOT}/etc/amazon/amazon-cloudwatch-agent
ln -f -s /opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/etc ${RPM_BUILD_ROOT}/etc/amazon/cwagent-otel-collector
# log
mkdir -p ${RPM_BUILD_ROOT}/var/log/amazon
ln -f -s /opt/aws/amazon-cloudwatch-agent/logs ${RPM_BUILD_ROOT}/var/log/amazon/amazon-cloudwatch-agent
ln -f -s /opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/logs ${RPM_BUILD_ROOT}/var/log/amazon/cwagent-otel-collector
# pid
mkdir -p ${RPM_BUILD_ROOT}/var/run/amazon
ln -f -s /opt/aws/amazon-cloudwatch-agent/var ${RPM_BUILD_ROOT}/var/run/amazon/amazon-cloudwatch-agent
ln -f -s /opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/var ${RPM_BUILD_ROOT}/var/run/amazon/cwagent-otel-collector

%files
%dir /opt/aws/amazon-cloudwatch-agent
%dir /opt/aws/amazon-cloudwatch-agent/bin
%dir /opt/aws/amazon-cloudwatch-agent/doc
%dir /opt/aws/amazon-cloudwatch-agent/etc
%dir /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d
%dir /opt/aws/amazon-cloudwatch-agent/logs
%dir /opt/aws/amazon-cloudwatch-agent/var
%dir /opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/etc
%dir /opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/etc/cwagent-otel-collector.d
%dir %attr(-, cwagent, cwagent) /opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/logs
%dir %attr(-, cwagent, cwagent) /opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/var
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl
/opt/aws/amazon-cloudwatch-agent/bin/CWAGENT_VERSION
/opt/aws/amazon-cloudwatch-agent/bin/config-translator
/opt/aws/amazon-cloudwatch-agent/bin/config-downloader
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
/opt/aws/amazon-cloudwatch-agent/bin/start-amazon-cloudwatch-agent
/opt/aws/amazon-cloudwatch-agent/bin/cwagent-otel-collector
/opt/aws/amazon-cloudwatch-agent/doc/amazon-cloudwatch-agent-schema.json
%config(noreplace) /opt/aws/amazon-cloudwatch-agent/etc/common-config.toml
/opt/aws/amazon-cloudwatch-agent/cwagent-otel-collector/var/.predefined-config-data
/opt/aws/amazon-cloudwatch-agent/LICENSE
/opt/aws/amazon-cloudwatch-agent/NOTICE

/opt/aws/amazon-cloudwatch-agent/THIRD-PARTY-LICENSES
/opt/aws/amazon-cloudwatch-agent/RELEASE_NOTES
/etc/init/amazon-cloudwatch-agent.conf
/etc/systemd/system/amazon-cloudwatch-agent.service
/etc/init/cwagent-otel-collector.conf
/etc/systemd/system/cwagent-otel-collector.service

/usr/bin/amazon-cloudwatch-agent-ctl
/etc/amazon/amazon-cloudwatch-agent
/var/log/amazon/amazon-cloudwatch-agent
/var/run/amazon/amazon-cloudwatch-agent
/etc/amazon/cwagent-otel-collector
/var/log/amazon/cwagent-otel-collector
/var/run/amazon/cwagent-otel-collector

%pre
# Stop the agent before upgrades.
if [ $1 -ge 2 ]; then
    if [ -x /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl ]; then
        /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a prep-restart
        /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop
    fi
fi

if ! grep "^cwagent:" /etc/group >/dev/null 2>&1; then
    groupadd -r cwagent >/dev/null 2>&1
    echo "create group cwagent, result: $?"
fi

if ! id cwagent >/dev/null 2>&1; then
    useradd -r -M cwagent -d /home/cwagent -g cwagent -c "Cloudwatch Agent" -s $(test -x /sbin/nologin && echo /sbin/nologin || (test -x /usr/sbin/nologin && echo /usr/sbin/nologin || (test -x /bin/false && echo /bin/false || echo /bin/sh))) >/dev/null 2>&1
    echo "create user cwagent, result: $?"
fi

if ! grep "^aoc:" /etc/group >/dev/null 2>&1; then
    groupadd -r aoc >/dev/null 2>&1
    echo "create group aoc, result: $?"
fi

if ! id aoc >/dev/null 2>&1; then
     useradd -r -M aoc -d /home/aoc -g aoc -c "AWS OTel Collector" -s $(test -x /sbin/nologin && echo /sbin/nologin || (test -x /usr/sbin/nologin && echo /usr/sbin/nologin || (test -x /bin/false && echo /bin/false || echo /bin/sh))) >/dev/null 2>&1
     echo "create user aoc, result: $?"
else
     usermod aoc -c "AWS OTel Collector" -s $(test -x /sbin/nologin && echo /sbin/nologin || (test -x /usr/sbin/nologin && echo /usr/sbin/nologin || (test -x /bin/false && echo /bin/false || echo /bin/sh))) >/dev/null 2>&1
     echo "update user aoc, result: $?"
fi

%preun
# Stop the agent after uninstall
if [ $1 -eq 0 ] ; then
    if [ -x /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl ]; then
        /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a preun
    fi
fi

%posttrans
# restart agent after upgrade
if [ -x /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl ]; then
    /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a cond-restart
fi

%clean
