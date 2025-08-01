# -*- coding: utf-8 -*- #
# Copyright 2017 Google LLC. All Rights Reserved.
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
"""Command to list operations in a project and location."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.composer import operations_util as operations_api_util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.composer import flags
from googlecloudsdk.command_lib.composer import resource_args
from googlecloudsdk.core import resources


DETAILED_HELP = {
    'EXAMPLES':
        """\
          To list the environment operations in locations ``us-central1'' and
          ``europe-west3'', run:

            $ {command} --locations=us-central1,europe-west3
        """
}


@base.UniverseCompatible
class List(base.ListCommand):
  """Lists environment operations.

  Prints a table containing the following columns:
  * uuid
  * type
  * location
  * target environment
  * status
  * last updated timestamp
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def _GetUri(operation):
    r = resources.REGISTRY.ParseRelativeName(
        operation.name,
        collection='composer.projects.locations.operations',
        api_version='v1',
    )
    return r.SelfLink()

  @staticmethod
  def Args(parser):
    resource_args.AddLocationResourceArg(
        parser,
        'in which to list operations.',
        positional=False,
        required=arg_parsers.ArgRequiredInUniverse(
            default_universe=False, non_default_universe=True
        ),
        plural=True,
        help_supplement=(
            'If not specified, the location stored in the property '
            ' [composer/location] will be used.'
        ),
    )
    parser.display_info.AddFormat(
        'table[box]('
        'name.segment(5):label=UUID,'
        'metadata.operationType:label=TYPE,'
        'name.segment(3):label=LOCATION,'
        'metadata.resource.basename():label=TARGET_ENVIRONMENT,'
        'metadata.state:label=STATE,'
        'metadata.createTime:label=CREATE_TIME:reverse'
        ')')
    parser.display_info.AddUriFunc(List._GetUri)

  def Run(self, args):
    location_refs = flags.FallthroughToLocationProperty(
        args.CONCEPTS.locations.Parse(),
        '--locations',
        'One or more locations in which to list operations must be provided.')

    return operations_api_util.List(
        location_refs,
        args.page_size,
        limit=args.limit,
        release_track=self.ReleaseTrack())
