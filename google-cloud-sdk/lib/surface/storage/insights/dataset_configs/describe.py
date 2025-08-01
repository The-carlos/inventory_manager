# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implementation of describe command for Insights dataset config."""

from googlecloudsdk.api_lib.storage import insights_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage.insights.dataset_configs import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Describe dataset config for Insights."""

  detailed_help = {
      'DESCRIPTION': """
      Describe the Insights dataset config.
      """,
      'EXAMPLES': """

      To describe a dataset config with config name "my_config" in location
      "us-central1":

          $ {command} my_config --location=us-central1

      To describe the same dataset config with fully specified name:

          $ {command} projects/foo/locations/us-central1/datasetConfigs/my_config
      """,
  }

  @staticmethod
  def Args(parser):
    resource_args.add_dataset_config_resource_arg(parser, 'to describe')

  def Run(self, args):
    dataset_config_ref = args.CONCEPTS.dataset_config.Parse()
    return insights_api.InsightsApi().get_dataset_config(
        dataset_config_ref.RelativeName()
    )
