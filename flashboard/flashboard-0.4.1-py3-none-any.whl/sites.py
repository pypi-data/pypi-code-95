import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from tournamentcontrol.competition.decorators import competition_by_slug_m
from tournamentcontrol.competition.models import Match
from tournamentcontrol.competition.sites import CompetitionSite

from flashboard.forms import FlashConfigurationForm

logger = logging.getLogger(__name__)


class FlashSite(CompetitionSite):

    kwargs_form_class = FlashConfigurationForm

    def __init__(self, name="scoreboard", app_name="scoreboard", **kwargs):
        super(FlashSite, self).__init__(name=name, app_name=app_name, **kwargs)

    @classmethod
    def verbose_name(cls):
        return u"Scoreboard"

    @competition_by_slug_m
    def division(self, request, competition, season, division, extra_context, **kwargs):
        # determine the next division listed after the current one, returning
        # to the start of the list if we're at the end
        try:
            next_division = season.divisions.filter(order__gt=division.order).earliest(
                "order"
            )
        except ObjectDoesNotExist:
            next_division = season.divisions.earliest("order")

        now = timezone.now()

        # get last two matches played by all teams in this division
        results = set()
        for team in division.teams.all():
            try:
                matches = team.matches.filter(
                    home_team_score__isnull=False,
                    away_team_score__isnull=False,
                    datetime__lt=now,
                )
                results.update(matches.order_by("-datetime")[:2])
            except ObjectDoesNotExist:
                logger.debug("No past dated matches for %r", team)

        # get next match to be played by all teams in this division
        upcoming = set()
        for team in division.teams.all():
            try:
                matches = team.matches.filter(datetime__gt=now)
                upcoming.add(matches[0])
            except IndexError:
                logger.debug("No future dated matches for %r", team)

        results = Match.objects.filter(pk__in=[r.pk for r in results])
        upcoming = Match.objects.filter(pk__in=[u.pk for u in upcoming])

        # extend the context
        extra_context.update(
            {
                "results": results,
                "upcoming": upcoming,
                "next": next_division,
            }
        )

        templates = self.template_path(
            "division.html", competition.slug, season.slug, division.slug
        )
        res = self.generic_detail(
            request,
            season.divisions,
            slug=division.slug,
            templates=templates,
            extra_context=extra_context,
        )

        # set delay and destination of reload
        delay = self.kwargs.get("delay", 0)
        if delay:
            redirect_to = self.reverse(
                "division",
                kwargs={
                    "competition": next_division.season.competition.slug,
                    "season": next_division.season.slug,
                    "division": next_division.slug,
                },
            )
            res["Refresh"] = "%d; url=%s" % (delay, redirect_to)

        return res
