from flask import render_template, make_response, jsonify, redirect, current_app, request, url_for
from flask_login import login_required, current_user
from tourtracker_app import db
from tourtracker_app.models.auth_models import User
from tourtracker_app.models.strava_api_models import StravaAccessToken
from tourtracker_app.main import bp
from tourtracker_app.main.forms import StravaActivitiesForm
import polyline
from urllib.parse import urlencode
import requests
from datetime import datetime



@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_profile'))
    return render_template('index.html')


@bp.route('/profile')
@login_required
def user_profile():
    form = StravaActivitiesForm()

    if current_user.strava_athlete_id is not None: # TODO probably a better/more robust way to do this
        strava_authenticated = True
    else:
        strava_authenticated = False

    return render_template('user_profile.html', email=current_user.email, strava_authenticated=strava_authenticated, form=form) #TODO put in logic for if we are not linked to strava


@bp.route('/get_activities', methods=['POST'])
def get_activities():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=utf-8':
        return 'Content Type not supported!'
    json = request.json
    date_format = "%Y-%m-%d"
    epoch = datetime(1970,1,1)
    start_date = json['startDate']
    end_date = json['endDate']
    start_timestamp = (datetime.strptime(start_date, date_format) - epoch).total_seconds()
    end_timestamp = (datetime.strptime(end_date, date_format) - epoch).total_seconds()
    base_url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': 'Bearer ' + current_user.strava_access_token[0].access_token}
    params = dict(before=end_timestamp, after=start_timestamp, page=1, per_page=30) #TODO results per page and nmber of pages?
    activities = []
    while True:
        full_url = base_url + ("?" + urlencode(params) if params else "") #TODO check if token is valid
        response = requests.get(full_url, headers=headers)
        response = response.json()
        print(response)
        if (not response):
            break
        for activity in response:
            latlong = []
            points = polyline.decode(activity['map']['summary_polyline'])
            for point in points:
                latlong.append({'lat': point[0], 'lng': point[1]})
            activities.append({'activity_id': activity['id'], 'points': latlong})
            params['page'] += 1
    return make_response(activities, 200)

    


    # print(response.json())
    

    
    
    





        # st_polyline = "gtbyHftmNgGeNaA{GcC^OGWaGE_FQ_@wAgAu@Kg@RWXuBjDsDxJUFmBmDmAmDY_@aQcHcGgCsAu@gLsEiAmAS_@JmCCWWnAu@NGSkDkq@LsFBwKl@om@A_G\\qb@R}D^cDvB}MhAgGx@wFbFqUz@eJb@_Df@wBpA{CbB{BrBwAhBs@vBYb@RvExGzAjDpCLRGr@mAv@YvBHbARr@\\\\CPe@j@}FxBf@`AAdBm@rByA\\Ap@Th@E`CuBfAoApMuRzFeHfEuDh@QX_@x@k@dEcC~GcF~HmIvAkBbFsI~A{BrB_CtBcBvBuAxC_B|CoA|Ba@rFWbCDnD`@hAX|FzBxBxArGfGdD|EfC~EnCvGbDbHvBfDnC`DxEfElBnAnCjAlARpCdAhARvCJj@GBK`A\\jAg@l@s@`H_DpAU\\D\\XNf@L?lFoDzBuB~EqGbNoSzGuKd]mh@bHcJdFwFdGoFvA}AlC{BtDqCz@c@`\\uUT_@`@C`EyBjWkKlFqCpCsB`GgFtAkBnBuB|BmDfEuHbCuFjCcHzLu`@`BwH|@eF~@_Hx@qJl@sFrAyPnBwRPkD`B_PRcDZ}B|Dmb@zA}P|@eFrAeGXsBdBmGnCkIrAsDt@yA`@IYH[b@{EzLoChKa@fCmAlFw@nFaBdPq@vJs@~FiBpRQpC{AvNc@lGc@fDa@lF_@rCuAdQgDjZeAbH}DvO}G`TaCfIaAfCmBhE}ExIuDlFeG~GaDrCaIzEmP|G{GjCkGjD}OpLqCbB_D`C_DjBkGhFiGhGiBzAuH~I_IvKoc@jq@yBrDsDfFkFdI_BrByAzAgCpBcDnBM?Me@OM_@AYUaAFkDbBuEpB[Jq@GK`@sBYmD{@}@?}AWwAa@cEmBcBaAsC_C_AeAsC_EgB{CoBiE{CyHcAsBaDqFi@q@kEcEyBmBiEaCqCaAuFaAyDI}Gh@wF~BwEzCiA~@mClCuIxMoDpEiCrCsHlGyFlDcAt@QXc@J}ExDoCrCsQ|WmDvDc@LuAYkBtAiAj@c@HsBEmAWK^a@vESb@_@D{Ai@qCUm@R_AtAQFsCM{@eCoA_CaBqBaAyAc@Uy@ZaBTcA`@uCxB}@lA}AtDq@rCa@jDe@hGaBlIgBtHiDzSU~@KzA{@jEm@rEYbFc@nf@DlCClBDjAw@|n@GPFZDrEIlCr@bL^fMvArVDLl@ENi@Fa@JTCnCLXjAhAxK`EhB`AzX~K^`@bBlE|AhCJALQzCeIdCmEjAq@`CzAH?NS@vEL`GJx@PHrBYx@`GLj@`GtM";
        # points = polyline.decode(st_polyline)
        # latlong = []
        # for point in points:
        #     latlong.append({'lat': point[0], 'lng': point[1]})
        # return make_response(latlong, 200)





        # if request.form.validate_on_submit():
        #     epoch = datetime(1970,1,1)
        #     date_format = "%Y-%m-%d"
        #     start_date = request.form.start_date
        #     end_date = request.form.end_date
        #     start_timestamp = (datetime.strptime(start_date, date_format) - epoch).total_seconds()
        #     end_timestamp = (datetime.strptime(end_date, date_format)- epoch).total_seconds()
        #     params = dict(before=end_timestamp, after=start_timestamp, page=1, per_page=3)
        #     full_url = base_url + ("?" + urlencode(params) if params else "")
        #     headers = {'Authorization': 'Bearer ' + 'ACCESS_CODE'}
        #     res = requests.get(full_url, headers=headers)
        #     print(res.json())
        #     return make_response(res, 200)
        #     #return render_template('user_profile.html')









    # st_polyline = "gtbyHftmNgGeNaA{GcC^OGWaGE_FQ_@wAgAu@Kg@RWXuBjDsDxJUFmBmDmAmDY_@aQcHcGgCsAu@gLsEiAmAS_@JmCCWWnAu@NGSkDkq@LsFBwKl@om@A_G\\qb@R}D^cDvB}MhAgGx@wFbFqUz@eJb@_Df@wBpA{CbB{BrBwAhBs@vBYb@RvExGzAjDpCLRGr@mAv@YvBHbARr@\\\\CPe@j@}FxBf@`AAdBm@rByA\\Ap@Th@E`CuBfAoApMuRzFeHfEuDh@QX_@x@k@dEcC~GcF~HmIvAkBbFsI~A{BrB_CtBcBvBuAxC_B|CoA|Ba@rFWbCDnD`@hAX|FzBxBxArGfGdD|EfC~EnCvGbDbHvBfDnC`DxEfElBnAnCjAlARpCdAhARvCJj@GBK`A\\jAg@l@s@`H_DpAU\\D\\XNf@L?lFoDzBuB~EqGbNoSzGuKd]mh@bHcJdFwFdGoFvA}AlC{BtDqCz@c@`\\uUT_@`@C`EyBjWkKlFqCpCsB`GgFtAkBnBuB|BmDfEuHbCuFjCcHzLu`@`BwH|@eF~@_Hx@qJl@sFrAyPnBwRPkD`B_PRcDZ}B|Dmb@zA}P|@eFrAeGXsBdBmGnCkIrAsDt@yA`@IYH[b@{EzLoChKa@fCmAlFw@nFaBdPq@vJs@~FiBpRQpC{AvNc@lGc@fDa@lF_@rCuAdQgDjZeAbH}DvO}G`TaCfIaAfCmBhE}ExIuDlFeG~GaDrCaIzEmP|G{GjCkGjD}OpLqCbB_D`C_DjBkGhFiGhGiBzAuH~I_IvKoc@jq@yBrDsDfFkFdI_BrByAzAgCpBcDnBM?Me@OM_@AYUaAFkDbBuEpB[Jq@GK`@sBYmD{@}@?}AWwAa@cEmBcBaAsC_C_AeAsC_EgB{CoBiE{CyHcAsBaDqFi@q@kEcEyBmBiEaCqCaAuFaAyDI}Gh@wF~BwEzCiA~@mClCuIxMoDpEiCrCsHlGyFlDcAt@QXc@J}ExDoCrCsQ|WmDvDc@LuAYkBtAiAj@c@HsBEmAWK^a@vESb@_@D{Ai@qCUm@R_AtAQFsCM{@eCoA_CaBqBaAyAc@Uy@ZaBTcA`@uCxB}@lA}AtDq@rCa@jDe@hGaBlIgBtHiDzSU~@KzA{@jEm@rEYbFc@nf@DlCClBDjAw@|n@GPFZDrEIlCr@bL^fMvArVDLl@ENi@Fa@JTCnCLXjAhAxK`EhB`AzX~K^`@bBlE|AhCJALQzCeIdCmEjAq@`CzAH?NS@vEL`GJx@PHrBYx@`GLj@`GtM";
    # points = polyline.decode(st_polyline)
    # latlong = []
    # for point in points:
    #     latlong.append({'lat': point[0], 'lng': point[1]})
    # return jsonify(latlong=latlong)

    
