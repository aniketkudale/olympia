import jinja2

from jingo import register
from tower import ugettext as _

from . import buttons
from amo.utils import chunked


register.function(buttons.install_button)
register.function(buttons.big_install_button)
register.function(buttons.mobile_install_button)


@register.filter
@jinja2.contextfilter
def statusflags(context, addon):
    """unreviewed/featuredaddon status flags for use as CSS classes"""
    app = context['APP']
    lang = context['LANG']
    if addon.is_unreviewed():
        return 'unreviewed'
    elif addon.is_featured(app, lang):
        return 'featuredaddon'
    else:
        return ''


@register.filter
@jinja2.contextfilter
def flag(context, addon):
    """unreviewed/featuredaddon flag heading."""
    status = statusflags(context, addon)
    msg = {'unreviewed': _('Not Reviewed'), 'featuredaddon': _('Featured')}
    if status:
        return jinja2.Markup(u'<h5 class="flag">%s</h5>' % msg[status])
    else:
        return ''


@register.inclusion_tag('addons/impala/dependencies_note.html')
@jinja2.contextfunction
def dependencies_note(context, addon, module_context='impala'):
    return new_context(**locals())


@register.inclusion_tag('addons/contribution.html')
@jinja2.contextfunction
def contribution(context, addon, text=None, src='', show_install=False,
                 show_help=True, large=False, contribution_src=None):
    """
    Show a contribution box.

    Parameters:
        addon
        text: The begging text at the top of the box.
        src: The page where the contribution link is coming from.
        show_install: Whether or not to show the install button.
        show_help: Show "What's this?" link?
        contribution_src: The source for the contribution src,
                          will use src if not provided.
    """
    if not contribution_src:
        contribution_src = src
    has_suggested = bool(addon.suggested_amount)
    return new_context(**locals())


@register.inclusion_tag('addons/impala/contribution.html')
@jinja2.contextfunction
def impala_contribution(context, addon, text=None, src='', show_install=False,
                        show_help=True, large=False, contribution_src=None):
    """
    Show a contribution box.

    Parameters:
        addon
        text: The begging text at the top of the box.
        src: The page where the contribution link is coming from.
        show_install: Whether or not to show the install button.
        show_help: Show "What's this?" link?
        contribution_src: The source for the contribution src,
                          will use src if not provided.
    """
    if not contribution_src:
        contribution_src = src
    has_suggested = bool(addon.suggested_amount)
    return new_context(**locals())


@register.inclusion_tag('addons/review_list_box.html')
@jinja2.contextfunction
def review_list_box(context, addon, reviews):
    """Details page: Show a box with three add-on reviews."""
    c = dict(context.items())
    c.update(addon=addon, reviews=reviews)
    return c


@register.inclusion_tag('addons/impala/review_list_box.html')
@jinja2.contextfunction
def impala_review_list_box(context, addon, reviews):
    """Details page: Show a box with three add-on reviews."""
    c = dict(context.items())
    c.update(addon=addon, reviews=reviews)
    return c


@register.inclusion_tag('addons/review_add_box.html')
@jinja2.contextfunction
def review_add_box(context, addon):
    """Details page: Show a box for the user to post a review."""
    c = dict(context.items())
    c['addon'] = addon
    return c


@register.inclusion_tag('addons/impala/review_add_box.html')
@jinja2.contextfunction
def impala_review_add_box(context, addon):
    """Details page: Show a box for the user to post a review."""
    c = dict(context.items())
    c['addon'] = addon
    return c


@register.inclusion_tag('addons/tags_box.html')
@jinja2.contextfunction
def tags_box(context, addon, tags=None):
    """
    Details page: Show a box with existing tags along with a form to add new
    ones.
    """
    c = dict(context.items())
    c.update({'addon': addon,
              'tags': tags})
    return c


@register.inclusion_tag('addons/listing/items.html')
@jinja2.contextfunction
def addon_listing_items(context, addons, show_date=False,
                        show_downloads=False, src=None, notes={}):
    return new_context(**locals())


@register.inclusion_tag('addons/impala/listing/items.html')
@jinja2.contextfunction
def impala_addon_listing_items(context, addons, field=None, src=None,
                               dl_src=None, notes={}):
    if not src:
        src = context.get('src')
    if not dl_src:
        dl_src = context.get('dl_src', src)
    return new_context(**locals())


@register.inclusion_tag('addons/listing/items_compact.html')
@jinja2.contextfunction
def addon_listing_items_compact(context, addons, show_date=False, src=None):
    return new_context(**locals())


@register.inclusion_tag('addons/listing/items_mobile.html')
@jinja2.contextfunction
def addon_listing_items_mobile(context, addons, sort=None, src=None):
    return new_context(**locals())


@register.inclusion_tag('addons/listing_header.html')
@jinja2.contextfunction
def addon_listing_header(context, url_base, sort_opts, selected):
    return new_context(**locals())


@register.inclusion_tag('addons/impala/listing/sorter.html')
@jinja2.contextfunction
def impala_addon_listing_header(context, url_base, sort_opts={}, selected=None,
                                extra_sort_opts={}, search_filter=None):
    if search_filter:
        selected = search_filter.field
        sort_opts = search_filter.opts
        if hasattr(search_filter, 'extras'):
            extra_sort_opts = search_filter.extras
    # When an "extra" sort option becomes selected, it will appear alongside
    # the normal sort options.
    old_extras = extra_sort_opts
    sort_opts, extra_sort_opts = list(sort_opts), []
    for k, v in old_extras:
        if k == selected:
            sort_opts.append((k, v, True))
        else:
            extra_sort_opts.append((k, v))
    return new_context(**locals())


@register.filter
@jinja2.contextfilter
@register.inclusion_tag('addons/impala/sidebar_listing.html')
def sidebar_listing(context, addon):
    return new_context(**locals())


@register.filter
@jinja2.contextfilter
@register.inclusion_tag('addons/impala/addon_hovercard.html')
def addon_hovercard(context, addon, lazyload=False, src=None, dl_src=None):
    if not src:
        src = context.get('src')
    if not dl_src:
        dl_src = context.get('dl_src', src)
    vital_summary = context.get('vital_summary') or 'rating'
    vital_more = context.get('vital_more')
    if 'vital_more' not in context:
        vital_more = 'adu'
    return new_context(**locals())


@register.filter
@jinja2.contextfilter
@register.inclusion_tag('addons/impala/addon_grid.html')
def addon_grid(context, addons, src=None, dl_src=None, pagesize=6, cols=2,
               vital_summary='rating', vital_more='adu'):
    if not src:
        src = context.get('src')
    # dl_src is an optional src parameter just for the download links
    if not dl_src:
        dl_src = context.get('dl_src', src)
    pages = chunked(addons, pagesize)
    columns = 'cols-%d' % cols
    return new_context(**locals())


@register.filter
@jinja2.contextfilter
@register.inclusion_tag('addons/impala/featured_grid.html')
def featured_grid(context, addons, src=None, dl_src=None, pagesize=3, cols=3):
    if not src:
        src = context.get('src')
    # dl_src is an optional src paramater just for the download links
    if not dl_src:
        dl_src = src
    pages = chunked(addons, pagesize)
    columns = '' if cols != 3 else 'three-col'
    return new_context(**locals())


@register.filter
@jinja2.contextfilter
@register.inclusion_tag('addons/impala/toplist.html')
def addon_toplist(context, addons, vital='users', src=None):
    return new_context(**locals())


def new_context(context, **kw):
    c = dict(context.items())
    c.update(kw)
    return c


@register.inclusion_tag('addons/persona_preview.html')
@jinja2.contextfunction
def persona_preview(context, persona, size='large', linked=True, extra=None,
                    details=False, title=False, caption=False, url=None):
    preview_map = {'large': persona.preview_url,
                   'small': persona.thumb_url}
    addon = persona.addon
    c = dict(context.items())
    c.update({'persona': persona, 'addon': addon, 'linked': linked,
              'size': size, 'preview': preview_map[size], 'extra': extra,
              'details': details, 'title': title, 'caption': caption,
              'url_': url})
    return c


@register.inclusion_tag('addons/mobile/persona_preview.html')
@jinja2.contextfunction
def mobile_persona_preview(context, persona):
    addon = persona.addon
    c = dict(context.items())
    c.update({'persona': persona, 'addon': addon})
    return c


@register.inclusion_tag('addons/mobile/persona_confirm.html')
@jinja2.contextfunction
def mobile_persona_confirm(context, persona, size='large'):
    addon = persona.addon
    c = dict(context.items())
    c.update({'persona': persona, 'addon': addon, 'size': size})
    return c


@register.inclusion_tag('addons/persona_grid.html')
@jinja2.contextfunction
def persona_grid(context, addons):
    return new_context(**locals())


@register.filter
@jinja2.contextfilter
@register.inclusion_tag('addons/impala/persona_grid.html')
def impala_persona_grid(context, personas, src=None, pagesize=6, cols=3):
    c = dict(context.items())
    return dict(pages=chunked(personas, pagesize),
                columns='cols-%d' % cols, **c)


@register.filter
@jinja2.contextfilter
@register.inclusion_tag('addons/impala/theme_grid.html')
def theme_grid(context, themes, src=None, dl_src=None):
    src = context.get('src', src)
    if not dl_src:
        dl_src = context.get('dl_src', src)
    return new_context(**locals())


@register.inclusion_tag('addons/report_abuse.html')
@jinja2.contextfunction
def addon_report_abuse(context, hide, addon):
    return new_context(**locals())
