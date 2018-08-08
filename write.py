import sys
import jinja2
import numpy as np
import os
import pandas as pd
import csv
import collections
import matplotlib.pyplot as plt
import sqlite3 as lite
from itertools import cycle
import matplotlib
from matplotlib import cm
import pyne
from pyne import nucname
from operator import itemgetter


def write_csv(header, raw_input, filename='csv-data.csv'):
    """Writes a csv file given the header, data, and the desired name of the
        csv file

    Parameters
    ----------
    header: list
        list of strings of the headers for the csv file
    data_input: csv data
        data to be added to csv file
    filename: string
        output file name, default: 'csv-data.csv'

    Returns
    -------
    Notes
    -------
    note:  this function expects raw data in the form of [[a1, a2, ... , aN],[b1, b2, ... ,bN]...[n1, n2, nN]],
            but it will put this data in the form of [[a1,b1,...,n1],[a2,b2,...,n2],...,[aN,bN,...,nN]] before
            writing it to the csv file.  Additionally, please be sure that the order of data in the raw input
            matches the order of headers.  Using the previous example of an arbitrary raw input, the header
            should be: ['header a','header b',...,'header n'].
    """
    if os.path.exists('./' + filename) is True:
        os.remove(filename)

    if isinstance(raw_input[0], list):

        data_input = []

        for element in range(len(raw_input[0])):
            data_input.append([])

        for element in range(len(raw_input[0])):
            for index in range(len(raw_input)):
                placeholder = raw_input[index]
                data_input[element].append(placeholder[element])

        with open(filename, 'a+') as file:
            w = csv.writer(file)
            w.writerow(header)
            for element in range(len(data_input)):
                w.writerow(data_input[element])

    else:
        with open(filename, 'a+') as file:
            w = csv.writer(file)
            w.writerow(header)
            w.writerow(raw_input)


def recipe(fresh_id, fresh_comp, spent_id, spent_comp):
    """Takes recipes for fresh and spent fuel, split into lists of isotope names and compostions, and
    organizes them into a dictionary in the key:value format

    Parameters
    ----------
    fresh_id: list
        isotope names in fresh fuel: list
    fresh_comp: list
        isotope compositions in fresh fuel
    spent_id: list
        isotope compostions in spent fuel

    Returns
    -------
    fresh: dict
        key:value fresh recipe format
    spent: dict
        key:value spent recipe format

    """

    assert len(fresh_id) == len(
        fresh_comp), 'The lengths of fresh_id and fresh_comp are not equal'
    assert len(spent_id) == len(
        spent_comp), 'The lengths of spent_id and spent_comp are not equal'

    fresh = {}
    for element in range(len(fresh_id)):
        fresh.update({fresh_id[element]: fresh_comp[element]})

    spent = {}
    for element in range(len(spent_id)):
        spent.update({spent_id[element]: spent_comp[element]})

    return fresh, spent


def load_template(template):
    """Reads a jinja2 template.

    Parameters
    ----------
    template: str
        filename of the desired jinja2 templatefresh_id: list

    Returns
    -------
    """
    with open(template, 'r') as input_template:
        output_template = jinja2.Template(input_template.read())

    return output_template


def write_reactor(
        reactor_data,
        reactor_template,
        output_name='rendered-reactor.xml'):
    """Writes a csv file given the header, data, and the desired name of the
        csv file

    Parameters
    ----------
    reactor_data: pandas dataframe
        reactor data
    reactor_template: str
        name of reactor template file
    output_name: str
        filename of rendered reactor input - default: 'rendered-reactor.xml'

    Returns
    -------

    """
    if os.path.exists('./' + output_name) is True:
        os.remove(output_name)

    template = load_template(reactor_template)

    PWR_cond = {'assem_size': 33000, 'n_assem_core': 3, 'n_assem_batch': 1}

    BWR_cond = {'assem_size': 33000, 'n_assem_core': 3, 'n_assem_batch': 1}

    reactor_data = reactor_data.drop(['Country', 'Operator'], 'columns')
    reactor_data = reactor_data.drop_duplicates()

    if len(reactor_data) == 1:

        if reactor_data.iloc[0, :].loc['Type'] == 'PWR':
            reactor_body = template.render(
                reactor_name=reactor_data.iloc[0, :].loc['Reactor Name'],
                assem_size=PWR_cond['assem_size'],
                n_assem_core=PWR_cond['n_assem_core'],
                n_assem_batch=PWR_cond['n_assem_batch'],
                capacity=reactor_data.iloc[0, :].loc['Net Electric Capacity'])

            with open(output_name, 'a+') as output:
                output.write(reactor_body)

        elif reactor_data.iloc[0, :].loc['Type'] == 'BWR':
            reactor_body = template.render(
                reactor_name=reactor_data.iloc[0, :].loc['Reactor Name'],
                assem_size=BWR_cond['assem_size'],
                n_assem_core=BWR_cond['n_assem_core'],
                n_assem_batch=BWR_cond['n_assem_batch'],
                capacity=reactor_data.iloc[0, :].loc['Net Electric Capacity'])

            with open(output_name, 'a+') as output:
                output.write(reactor_body)

        else:
            print(
                'Warning: specifications of this reactor type have not been given.  Using placeholder values.')

            reactor_body = template.render(
                reactor_name=reactor_data.iloc[0, :].loc['Reactor Name'],
                assem_size=PWR_cond['assem_size'],
                n_assem_core=PWR_cond['n_assem_core'],
                n_assem_batch=PWR_cond['n_assem_batch'],
                capacity=reactor_data.iloc[0, :].loc['Net Electric Capacity'])

            with open(output_name, 'a+') as output:
                output.write(reactor_body)

    else:
        for element in range(len(reactor_data)):

            if reactor_data.iloc[element, :].loc['Type'] == 'PWR':
                reactor_body = template.render(
                    reactor_name=reactor_data.iloc[
                        element,
                        :].loc['Reactor Name'],
                    assem_size=PWR_cond['assem_size'],
                    n_assem_core=PWR_cond['n_assem_core'],
                    n_assem_batch=PWR_cond['n_assem_batch'],
                    capacity=reactor_data.iloc[
                        element,
                        :].loc['Net Electric Capacity'])

                with open(output_name, 'a+') as output:
                    output.write(reactor_body + "\n \n")

            elif reactor_data.iloc[element, :].loc['Type'] == 'BWR':
                reactor_body = template.render(
                    reactor_name=reactor_data.iloc[
                        element,
                        :].loc['Reactor Name'],
                    assem_size=BWR_cond['assem_size'],
                    n_assem_core=BWR_cond['n_assem_core'],
                    n_assem_batch=BWR_cond['n_assem_batch'],
                    capacity=reactor_data.iloc[
                        element,
                        :].loc['Net Electric Capacity'])

                with open(output_name, 'a+') as output:
                    output.write(reactor_body + "\n \n")

            else:
                print(
                    'Warning: specifications of this reactor type have not been given.  Using placeholder values.')

                reactor_body = template.render(
                    reactor_name=reactor_data.iloc[
                        element,
                        :].loc['Reactor Name'],
                    assem_size=PWR_cond['assem_size'],
                    n_assem_core=PWR_cond['n_assem_core'],
                    n_assem_batch=PWR_cond['n_assem_batch'],
                    capacity=reactor_data.iloc[
                        element,
                        :].loc['Net Electric Capacity'])

                with open(output_name, 'a+') as output:
                    output.write(reactor_body + "\n \n")
    return output_name


def write_region(
        reactor_data,
        deployment_data,
        region_template,
        output_name='rendered-region.xml'):
    """Renders the region portion of the Cyclus input file.

    Parameters
    ----------
    reactor_data: pandas dataframe
        reactor data
    deployment data: dict
        dictionary object giving values for initial deployment of each facility type,
        key names: n_mine, n_enrichment, n_reactor, n_repository
    region_template: str
        name of region template file
    output_name: str
        filenname of rendered region, default: 'rendered-region.xml'
    Returns
    -------
    rendered region input filename: str
        filename of rendered region

    """

    if os.path.exists('./' + output_name) is True:
        os.remove(output_name)

    template = load_template(region_template)

    reactor_data = reactor_data.drop(['Type'], 'columns')
    reactor_data = reactor_data.groupby(
        reactor_data.columns.tolist()).size().reset_index().rename(
        columns={
            0: 'Number Reactors'})

    country_reactors = {}
    countries_keys = reactor_data.loc[:, 'Country'].drop_duplicates()
    operator_keys = reactor_data.loc[:, 'Operator'].drop_duplicates()

    for country in countries_keys.tolist():

        country_operators = {}
        for operator in operator_keys.tolist():

            reactor_dict = {}
            data_loop = reactor_data.query(
                'Country == @country & Operator == @operator ')

            for element in range(len(data_loop)):
                reactor_dict[
                    data_loop.iloc[
                        element, :].loc['Reactor Name']] = [
                    data_loop.iloc[
                        element, :].loc['Number Reactors'], data_loop.iloc[
                        element, :].loc['Net Electric Capacity']]

            country_operators[operator] = reactor_dict

        country_reactors[country] = country_operators

    region_body = template.render(country_reactor_dict=country_reactors,
                                  countries_infra=deployment_data)

    with open(output_name, 'a+') as output:
        output.write(region_body)

    return output_name


def write_recipes(
        fresh,
        spent,
        recipe_template,
        output_name='rendered-recipe.xml'):
    """Renders the recipe portion of the Cyclus input file.

    Parameters
    ----------
    fresh: dict
        dictionary object, in id:comp format, containing the isotope names
        and compositions (in mass basis) for fresh fuel
    spent: dict
        dictionary object, in id:comp format, containing the isotope names
        and compositions (in mass basis) for spent  fuel
    recipe_template: str
        name of recipe template file
    output_name: str
        desired name of output file, default: 'rendered-recipe.xml'
    Returns
    -------

    """

    if os.path.exists('./' + output_name) is True:
        os.remove(output_name)

    template = load_template(recipe_template)

    recipe_body = template.render(
        fresh_fuel=fresh,
        spent_fuel=spent)

    with open(output_name, 'w') as output:
        output.write(recipe_body)

    return output_name


def write_main_input(
        simulation_parameters,
        reactor_file,
        region_file,
        recipe_file,
        input_template,
        output_name='rendered-main-input.xml'):
    """Renders the final, main input file for a Cyclus simulation.

    Parameters
    ----------
    simulation_parameters: list
        specifics of cyclus simulation, containing the data: [duration, start month, start year]
    reactor_file: str
        rendered reactor filename
    region_file: str
        rendered region filename
    recipe_file: str
        rendered recipe filename
    main_input_template: str
        name of main input template file
    output_name: str
        desired name of output file, default: 'rendered-main-input.xml'

    Returns
    -------
    """

    if os.path.exists('./' + output_name) is True:
        os.remove(output_name)

    template = load_template(input_template)

    with open(reactor_file, 'r') as reactorf:
        reactor = reactorf.read()

    with open(region_file, 'r') as regionf:
        region = regionf.read()

    with open(recipe_file, 'r') as recipef:
        recipe = recipef.read()

    main_input = template.render(
        duration=simulation_parameters[0],
        start_month=simulation_parameters[1],
        start_year=simulation_parameters[2],
        decay=simulation_parameters[3],
        reactor_input=reactor,
        region_input=region,
        recipe_input=recipe)

    with open(output_name, 'w') as output:
        output.write(main_input)


def import_csv(csv_file):
    """Imports the contents of a csv file as a dataframe.

    Parameters
    ----------
    csv_file: str
        name of the csv filename
    Returns
    -------
    reactor_data: pandas dataframe
        data contained in the csv file as a dataframe

    """
    reactor_data = (
        pd.read_csv(
            csv_file,
            names=[
                'Country',
                'Reactor Name',
                'Type',
                'Net Electric Capacity',
                'Operator'],
            skiprows=[0]))

    return reactor_data


if len(sys.argv) < 4:
    print('Usage: python write_input.py [csv]' +
          '[init_date] [duration] [output_file_name]')


def delete_file(file):
    """Deletes a file if it exists.

    Parameters
    ----------
    file: str
        filename to delete, if it exists

    Returns
    -------
    null

    """
    if os.path.exists('./' + file) is True:
        os.system('rm ' + file)


def read_csv(csv_file):
    """This function reads the csv file and returns the list.

    Parameters
    ---------
    csv_file: str
        csv file that lists country, reactor name, net_elec_capacity etc.

    Returns
    -------
    reactor_array:  list
        array with the data from csv file
    """
    reactor_array = np.genfromtxt(csv_file,
                                  skip_header=1,
                                  delimiter=',',
                                  dtype=('S128', 'S128',
                                         'S128', 'int',
                                         'S128', 'S128', 'int',
                                         'int', 'int',
                                         'int', 'int',
                                         'int', 'int',
                                         'int', 'float'),
                                  names=('country', 'reactor_name',
                                         'type', 'net_elec_capacity',
                                         'status', 'operator', 'const_date',
                                         'cons_year', 'first_crit',
                                         'entry_time', 'lifetime',
                                         'first_grid', 'commercial',
                                         'shutdown_date', 'ucf'))
    return filter_test_reactors(reactor_array)


def ymd(yyyymmdd):
    """This function extracts year and month value from yyyymmdd format

        The month value is rounded up if the day is above 16

    Parameters
    ---------
    yyyymmdd: int
        date in yyyymmdd format

    Returns
    -------
    year: int
        year
    month: int
        month
    """

    year = yyyymmdd // 10000
    month = (yyyymmdd // 100) % 100
    day = yyyymmdd % 100
    if day > 16:
        month += 1
    return (year, month)


def protoype_lifetime(start_date, end_date):
    """This function gets the lifetime for a prototype given the
       start and end date.

    Parameters
    ---------
    start_date: int
        start date of reactor - first criticality.
    end_date: int
        end date of reactor - null if not listed or unknown

    Returns
    -------
    lifetime: int
        lifetime of the prototype in months

    """

    if end_date != -1:
        end_year, end_month = ymd(end_date)
        start_year, start_month = ymd(start_date)
        year_difference = end_year - start_year
        month_difference = end_month - start_month
        if month_difference < 0:
            year_difference -= 1
            start_month += 12
        month_difference = end_month - start_month

        return (12 * year_difference + month_difference)
    else:
        return 720


def get_entrytime(init_date, start_date):
    """This function converts the date format and saves it in variables.

        All dates are in format - yyyymmdd

    Parameters
    ---------
    init_date: int
        start date of simulation
    start_date: int
        start date of reactor - first criticality.

    Returns
    -------
    entry_time: int
        timestep of the prototype to enter

    """

    init_year, init_month = ymd(init_date)
    start_year, start_month = ymd(start_date)

    year_difference = start_year - init_year
    month_difference = start_month - init_month
    if month_difference < 0:
        year_difference -= 1
        start_month += 12
    month_difference = start_month - init_month

    entry_time = 12 * year_difference + month_difference

    return entry_time


def filter_test_reactors(reactor_array):
    """This function filters experimental reactors that have a
       net electricity capacity less than 100 MWe

    Parameters
    ---------
    reactor_array: list
        array with reactor data.

    Returns
    -------
    array
        array with the filtered data
    """
    test_reactors = []
    count = 0
    for data in reactor_array:
        if data['net_elec_capacity'] < 100:
            test_reactors.append(count)
        count += 1
    return np.delete(reactor_array, test_reactors)


def read_template(template):
    """ Returns a jinja template

    Parameters
    ---------
    template: str
        template file that is to be stored as variable.

    Returns
    -------
    output_template: jinja template object
        output template that can be 'jinja.render' -ed.

    """

    with open(template, 'r') as fp:
        input_template = fp.read()
        output_template = jinja2.Template(input_template)

    return output_template


def refine_name(name_data):
    """ Takes the name data and decodes and refines it.

    Parameters
    ----------
    name_data: str
        reactor name data from csv file

    Returns
    -------
    name: str
        refined and decoded name of reactor
    """
    name = name_data.decode('utf-8')
    start = name.find('(')
    end = name.find(')')
    if start != -1 and end != -1:
        name = name[:start]
    return name


def reactor_render(reactor_data, output_file, is_cyborg=False):
    """Takes the list and template and writes a reactor file

    Parameters
    ----------
    reactor_data: list
        list of data on reactors
    template: jinja.template
        jinja template for reactor file
    mox_template: jinja.template
        jinja template for mox reactor file
    output_file: str
        name of output file
    is_cyborg: bool
        if True, uses Cyborg templates

    Returns
    -------
    The reactor section of cyclus input file

    """

    template_path = '../templates/[reactor]_template_cyborg.xml.in'

    if not is_cyborg:
        template_path = template_path.replace('_cyborg', '')

    pwr_template = read_template(template_path.replace('[reactor]', 'pwr'))
    mox_reactor_template = read_template(
        template_path.replace('[reactor]', 'mox'))
    candu_template = read_template(template_path.replace('[reactor]', 'candu'))

    ap1000_spec = {'template': pwr_template,
                   'kg_per_assembly': 446.0,
                   'assemblies_per_core': 157,
                   'assemblies_per_batch': 52}
    bwr_spec = {'template': pwr_template,
                'kg_per_assembly': 180,
                'assemblies_per_core': int(764 / 1000),
                'assemblies_per_batch': int(764 / 3000)}
    phwr_spec = {'template': candu_template,
                 'kg_per_assembly': 8000 / 473,
                 'assemblies_per_core': int(473 / 500),
                 'assemblies_per_batch': 60}
    candu_spec = {'template': candu_template,
                  'kg_per_assembly': 8000 / 473,
                  'assemblies_per_core': int(473 / 500),
                  'assemblies_per_batch': 60}
    pwr_spec = {'template': pwr_template,
                'kg_per_assembly': 446.0,
                'assemblies_per_core': int(193 / 1000),
                'assemblies_per_batch': int(193 / 3000)}
    epr_spec = {'template': pwr_template,
                'kg_per_assembly': 467.0,
                'assemblies_per_core': 216,
                'assemblies_per_batch': 72}

    reactor_specs = {'AP1000': ap1000_spec,
                     'PHWR': phwr_spec,
                     'BWR': bwr_spec,
                     'CANDU': candu_spec,
                     'PWR': pwr_spec,
                     'EPR': epr_spec}

    for data in reactor_data:
        name = refine_name(data['reactor_name'])
        reactor_type = data['type'].decode('utf-8')
        if reactor_type in reactor_specs.keys():
            spec_dict = reactor_specs[reactor_type]
            reactor_body = spec_dict['template'].render(
                country=data['country'].decode('utf-8'),
                type=reactor_type,
                reactor_name=name,
                assem_size=round(spec_dict['kg_per_assembly'], 3),
                n_assem_core=int(round(spec_dict['assemblies_per_core']
                                       * data['net_elec_capacity'])),
                n_assem_batch=int(round(spec_dict['assemblies_per_batch']
                                        * data['net_elec_capacity'])),
                capacity=data['net_elec_capacity'])
        else:
            reactor_body = pwr_template.render(
                country=data['country'].decode('utf-8'),
                reactor_name=name,
                type=reactor_type,
                assem_size=523.4,
                n_assem_core=int(
                    round(data['net_elec_capacity'] / 1000 * 193)),
                n_assem_batch=int(
                    round(data['net_elec_capacity'] / 3000 * 193)),
                capacity=data['net_elec_capacity'])

        with open(output_file, 'a') as output:
            output.write(reactor_body)


def input_render(init_date, duration, reactor_file,
                 region_file, output_file, reprocessing):
    """Creates total input file from region and reactor file

    Parameters
    ---------
    init_date: int
        date of desired start of simulation (format yyyymmdd)
    reactor_file: str
        jinja rendered reactor section of cyclus input file
    region_file: str
        jinja rendered region section of cylcus input file
    output_file: str
        name of output file
    reprocessing: bool
        True if reprocessing is done, false if ignored

    Returns
    -------
    A complete cylus input file.

    """
    template = read_template('../templates/input_template.xml.in')
    with open(reactor_file, 'r') as fp:
        reactor = fp.read()
    with open(region_file, 'r') as bae:
        region = bae.read()

    startyear, startmonth = ymd(init_date)

    if reprocessing is True:
        reprocessing_chunk = ('<entry>\n'
                              + '  <number>1</number>\n'
                              + '  <prototype>reprocessing</prototype>\n'
                              + '</entry>')
    else:
        reprocessing_chunk = ''
    rendered_template = template.render(duration=duration,
                                        startmonth=startmonth,
                                        startyear=startyear,
                                        reprocessing=reprocessing_chunk,
                                        reactor_input=reactor,
                                        region_input=region)

    with open(output_file, 'w') as output:
        output.write(rendered_template)

    os.system('rm reactor_output.xml.in region_output.xml.in')


def region_render(reactor_data, output_file):
    """Takes the list and template and writes a region file

    Parameters
    ---------
    reactor_data: list
        list of data on reactors
    output_file: str
        name of output file

    Returns
    -------
    The region section of cyclus input file

    """
    template = read_template('../templates/deployinst_template.xml.in')
    full_template = read_template('../templates/region_output_template.xml.in')
    country_list = []
    empty_country = []

    valhead = '<val>'
    valtail = '</val>'
    for data in reactor_data:
        country_list.append(data['country'].decode('utf-8'))
    country_set = set(country_list)

    for country in country_set:
        prototype = ''
        entry_time = ''
        n_build = ''
        lifetime = ''

        for data in reactor_data:
            if data['country'].decode('utf-8') == country:

                prototype += (valhead
                              + refine_name(data['reactor_name'])
                              + valtail + '\n')
                entry_time += (valhead
                               + str(data['entry_time']) + valtail + '\n')
                n_build += valhead + '1' + valtail + '\n'
                lifetime += valhead + str(data['lifetime']) + valtail + '\n'

        render_temp = template.render(prototype=prototype,
                                      start_time=entry_time,
                                      number=n_build,
                                      lifetime=lifetime)
        if len(render_temp) > 100:
            with open(country, 'a') as output:
                output.write(render_temp)
        else:
            empty_country.append(country)

    for country in empty_country:
        country_set.remove(country)

    for country in country_set:
        with open(country, 'r') as ab:
            country_input = ab.read()
            country_body = full_template.render(
                country=country,
                country_gov=(country
                             + '_government'),
                deployinst=country_input)

        with open(country + '_region', 'a') as output:
            output.write(country_body)

        os.system('cat ' + country + '_region >> ' + output_file)
        os.system('rm ' + country)
        os.system('rm ' + country + '_region')


def main(csv_file, init_date, duration, output_file, reprocessing=True):
    """ Generates cyclus input file from csv files and jinja templates.

    Parameters
    ---------
    csv_file : str
        csv file containing reactor data (country, name, net_elec_capacity)
    init_date: int
        yyyymmdd format of initial date of simulation
    input_template: str
        template file for entire complete cyclus input file
    output_file: str
        directory and name of complete cyclus input file
    reprocessing: bool
        True if reprocessing is done, False if not

    Returns
    -------
    File with reactor section of cyclus input file
    File with region section of cyclus input file
    File with complete cyclus input file

    """

    delete_file(output_file)
    reactor_output_filename = 'reactor_output.xml.in'
    region_output_filename = 'region_output.xml.in'
    csv_database = read_csv(csv_file)
    for data in csv_database:
        entry_time = get_entrytime(init_date, data['first_crit'])
        lifetime = protoype_lifetime(data['first_crit'], data['shutdown_date'])
        if entry_time <= 0:
            lifetime = lifetime + entry_time
            if lifetime < 0:
                lifetime = 0
            entry_time = 1
        data['entry_time'] = entry_time
        data['lifetime'] = lifetime
    reactor_render(csv_database, reactor_output_filename)
    region_render(csv_database, region_output_filename)
    input_render(init_date, duration, reactor_output_filename,
                 region_output_filename, output_file, reprocessing)


def read_locations(csv_file):
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        reactor_lat_lon = {}
        for row in reader:
            #print(row['reactor'],row['lat'], row['lon'])
            reactor_lat_lon[row['reactor']] = row['lat'], row['lon']
        return reactor_lat_lon
