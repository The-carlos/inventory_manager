# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Create public advertised prefix command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import public_advertised_prefixes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.public_advertised_prefixes import flags
from googlecloudsdk.command_lib.util.apis import arg_utils
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class Create(base.CreateCommand):
  r"""Creates a Compute Engine public advertised prefix.

  ## EXAMPLES

  To create a public advertised prefix:

    $ {command} my-public-advertised-prefix --range=120.120.10.0/24 \
      --dns-verification-ip=120.120.10.15

  To create a v2 public advertised prefix:

    $ {command} my-v2-public-advertised-prefix --range=120.120.10.0/24 \
      --dns-verification-ip=120.120.10.15 --pdp-scope=REGIONAL
  """

  _include_ipv6_access_type = False

  @classmethod
  def Args(cls, parser):
    flags.MakePublicAdvertisedPrefixesArg().AddArgument(parser)
    flags.AddCreatePapArgsToParser(parser, cls._include_ipv6_access_type)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    messages = holder.client.messages
    pap_client = public_advertised_prefixes.PublicAdvertisedPrefixesClient(
        holder.client, messages, holder.resources
    )
    pap_ref = flags.MakePublicAdvertisedPrefixesArg().ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(holder.client),
    )

    pap = messages.PublicAdvertisedPrefix
    input_ipv6_access_type = None
    if self._include_ipv6_access_type and args.ipv6_access_type:
      input_ipv6_access_type = arg_utils.ChoiceToEnum(
          args.ipv6_access_type,
          pap.Ipv6AccessTypeValueValuesEnum,
      )

    input_dns_verification_ip = None
    if args.dns_verification_ip:
      input_dns_verification_ip = args.dns_verification_ip

    result = pap_client.Create(
        pap_ref,
        ip_cidr_range=args.range,
        dns_verification_ip=input_dns_verification_ip,
        description=args.description,
        pdp_scope=pap.PdpScopeValueValuesEnum(args.pdp_scope)
        if args.pdp_scope
        else None,
        ipv6_access_type=input_ipv6_access_type,
    )
    log.CreatedResource(pap_ref.Name(), 'public advertised prefix')
    return result


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  r"""Create a public advertised prefix in the Beta release track.

  ## EXAMPLES

  To create a public advertised prefix:

    $ {command} my-public-advertised-prefix --range=120.120.10.0/24 \
      --dns-verification-ip=120.120.10.15

  To create a v2 public advertised prefix:

    $ {command} my-v2-public-advertised-prefix --range=120.120.10.0/24 \
      --dns-verification-ip=120.120.10.15 --pdp-scope=REGIONAL
  """

  _include_ipv6_access_type = False


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(CreateBeta):
  r"""Create a public advertised prefix in the Alpha release track.

  ## EXAMPLES

  To create a public advertised prefix:

    $ {command} my-public-advertised-prefix --range=120.120.10.0/24 \
      --dns-verification-ip=120.120.10.15

  To create a v2 public advertised prefix:

    $ {command} my-v2-public-advertised-prefix --range=120.120.10.0/24 \
      --dns-verification-ip=120.120.10.15 --pdp-scope=REGIONAL
  """

  _include_ipv6_access_type = True
