// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT

// +build windows

package windows_event_log

import (
	"path/filepath"
	"strings"

	"time"

	"github.com/aws/amazon-cloudwatch-agent/internal/logscommon"
	"github.com/aws/amazon-cloudwatch-agent/logs"
	"github.com/aws/amazon-cloudwatch-agent/plugins/inputs/windows_event_log/wineventlog"
	"github.com/influxdata/telegraf"
	"github.com/influxdata/telegraf/plugins/inputs"
)

const (
	forcePullInterval = 250 * time.Millisecond
)

type EventConfig struct {
	Name          string   `toml:"event_name"`
	Levels        []string `toml:"event_levels"`
	RenderFormat  string   `toml:"event_format"`
	BatchReadSize int      `toml:"batch_read_size"`
	LogGroupName  string   `toml:"log_group_name"`
	LogStreamName string   `toml:"log_stream_name"`
	Destination   string   `toml:"destination"`
	Retention     int      `toml:"retention_in_days"`
}

type Plugin struct {
	FileStateFolder string        `toml:"file_state_folder"`
	Events          []EventConfig `toml:"event_config"`
	Destination     string        `toml:"destination"`

	newEvents []logs.LogSrc
}

func (s *Plugin) Description() string {
	return "A plugin to collect Windows event logs"
}

func (s *Plugin) SampleConfig() string {
	return `
	file_state_folder = "c:\\path\\to\\state\\folder"

	[[inputs.windows_event_log.event_config]]
	event_name = "System"
	event_levels = ["2", "3"]
	batch_read_size = 1
	log_group_name = "System"
	log_stream_name = "STREAM_NAME"
	destination = "cloudwatchlogs"
	`
}

func (s *Plugin) Gather(acc telegraf.Accumulator) (err error) {
	return nil
}

func (s *Plugin) FindLogSrc() []logs.LogSrc {
	events := s.newEvents
	s.newEvents = nil
	return events
}

/**
 * We can do any initialization in this method.
 */
func (s *Plugin) Start(acc telegraf.Accumulator) error {
	for _, eventConfig := range s.Events {
		stateFilePath := logscommon.WindowsEventLogPrefix + escapeFilePath(eventConfig.LogGroupName)
		destination := eventConfig.Destination
		if destination == "" {
			destination = s.Destination
		}
		eventLog := wineventlog.NewEventLog(
			eventConfig.Name,
			eventConfig.Levels,
			eventConfig.LogGroupName,
			eventConfig.LogStreamName,
			eventConfig.RenderFormat,
			destination,
			stateFilePath,
			eventConfig.BatchReadSize,
			eventConfig.Retention,
		)
		err := eventLog.Init()
		if err != nil {
			return err
		}
		s.newEvents = append(s.newEvents, eventLog)
	}
	return nil
}

func escapeFilePath(filePath string) string {
	escapedFilePath := filepath.ToSlash(filePath)
	escapedFilePath = strings.Replace(escapedFilePath, "/", "_", -1)
	escapedFilePath = strings.Replace(escapedFilePath, " ", "_", -1)
	escapedFilePath = strings.Replace(escapedFilePath, ":", "_", -1)
	return escapedFilePath
}

func (s *Plugin) Stop() {
}

func init() {
	inputs.Add("windows_event_log", func() telegraf.Input { return &Plugin{} })
}
