# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
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
"""Commands for reading and manipulating disks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class Disks(base.Group):
  """Read and manipulate Compute Engine disks."""


Disks.category = base.DISKS_CATEGORY

Disks.detailed_help = {
    'DESCRIPTION': """
        Read and manipulate Compute Engine disks.

        For more information about disks, see the
        [disks documentation](https://cloud.google.com/compute/docs/disks/).

        See also: [Disks API](https://cloud.google.com/compute/docs/reference/rest/v1/disks).
    """,
}
