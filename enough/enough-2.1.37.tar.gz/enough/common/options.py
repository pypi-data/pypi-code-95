def set_options(parser):
    parser.add_argument('--driver',
                        default='openstack',
                        choices=['libvirt', 'openstack'])
    parser.add_argument('--inventory', action='append')
    o = parser.add_argument_group(title='OpenStack',
                                  description='Only when --driver=openstack')
    o.add_argument(
        '--cloud',
        default='production',
        help='Name of the cloud in which resources are provisionned')
    parser.openstack_group = o
    return parser
